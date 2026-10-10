package com.lol.draft_lol.service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.lol.draft_lol.DTO.DraftAcaoDto;
import com.lol.draft_lol.DTO.DraftProxJogoDto;
import com.lol.draft_lol.DTO.DraftRequestDto;
import com.lol.draft_lol.DTO.DraftStartDto;
import com.lol.draft_lol.DTO.DraftSugestaoDto;
import com.lol.draft_lol.DTO.DraftSugestaoRequestDto;
import com.lol.draft_lol.DTO.SugestaoResponseDto;
import com.lol.draft_lol.client.PythonDraftClient;
import com.lol.draft_lol.exception.AcaoEmAndamentoException;
import com.lol.draft_lol.exception.LimiteExcedidoException;
import com.lol.draft_lol.model.DraftSessao;
import com.lol.draft_lol.model.Fase;
import com.lol.draft_lol.repository.DraftSessaoRepository;

@Service
public class DraftService {

  @Autowired
  private PythonDraftClient pythonClient;
  @Autowired
  private TimeService timeService;
  @Autowired
  private ChampionService championService;
  @Autowired
  private DraftSessaoRepository draftSessaoRepository;

  @Value("${draft.limite-sugestoes-por-sessao:100}")
  private int limiteSugestoesPorSessao;
  @Value("${draft.limite-sessoes-por-ip:10}")
  private int limiteSessoesPorIp;

  private final Map<String, Boolean> sessoesOcupadas = new ConcurrentHashMap<>();

  public Object criarDraft(DraftStartDto dados, String ipOrigem) {
    String liga = (dados.liga() == null || dados.liga().isBlank())
        ? "CBLOL" : dados.liga().trim().toUpperCase();
    List<String> timesLiga = listarTimesPorLiga(liga);

    String timeIA = timesLiga.stream()
        .filter(t -> t.equalsIgnoreCase(dados.timeIA()))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("Time não encontrado: " + dados.timeIA()));
    String timeUsuario = timesLiga.stream()
        .filter(t -> t.equalsIgnoreCase(dados.timeUsuario()))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("Time não encontrado: " + dados.timeUsuario()));

    if (dados.quantidadeJogos() == null) {
      throw new IllegalArgumentException("quantidadeJogos é obrigatório");
    }
    boolean isFirstPick = Boolean.TRUE.equals(dados.isFirstPick());

    DraftSessao sessao = new DraftSessao(
      UUID.randomUUID().toString(), timeUsuario, timeIA, liga, isFirstPick, dados.quantidadeJogos()
    );
    sessao.setIpOrigem(ipOrigem);
    if (!draftSessaoRepository.criar(sessao, limiteSessoesPorIp)) {
      throw new LimiteExcedidoException(
          "Limite de drafts simultâneos atingido para o seu IP. Finalize um draft ou tente mais tarde.");
    }

    return montarResposta(sessao);
  }

  public Object reiniciarJogo(DraftSugestaoDto dados) {
    return comTrava(dados.sessionId(), () -> {
      DraftSessao sessao = buscarSessao(dados.sessionId());
      sessao.registrarHistorico();     
      sessao.reiniciarJogoAtual();
      draftSessaoRepository.salvar(sessao);
      return montarResposta(sessao);
    });
  }


  public Object alterarDraft(DraftAcaoDto dados) {
    return comTrava(dados.sessionId(), () -> {
      DraftSessao sessao = buscarSessao(dados.sessionId());
      if (sessao.getFaseAtual() == Fase.FIM) {
        throw new IllegalArgumentException("Draft já finalizado");
      }

      String jogadorAtual = calcularJogadorAtual(sessao);
      boolean isBan = sessao.getFaseAtual().name().startsWith("BAN");

      String champion;
      if (dados.champion() != null) {
        if (!championService.existe(dados.champion())) {
          throw new IllegalArgumentException("Campeão não encontrado: " + dados.champion());
        }
        champion = championService.normalizar(dados.champion());
        if (sessao.campeaoIndisponivel(champion)) {
          throw new IllegalArgumentException("Campeão indisponível: " + champion);
        }
      } else {
        SugestaoResponseDto resposta = pythonClient.pedirAcao(montarRequest(sessao, jogadorAtual));
        champion = primeiroCampeao(resposta.champion());
      }
      sessao.registrarHistorico();
      aplicarAcao(sessao, jogadorAtual, isBan, champion);
      sessao.setFaseAtual(sessao.getFaseAtual().proximaFase(sessao.isFirstPick()).fase());
      draftSessaoRepository.salvar(sessao);

      return montarResposta(sessao);
    });
  }

  public Object proxJogo(DraftProxJogoDto dados) {
    return comTrava(dados.sessionId(), () -> {
      DraftSessao sessao = buscarSessao(dados.sessionId());
      if (sessao.getGameAtual() >= sessao.getTotalJogos()) {
        throw new IllegalArgumentException("Draft já finalizado");
      }
      if (sessao.getFaseAtual() != Fase.FIM) {
        throw new IllegalArgumentException("Jogo não finalizado");
      }

      sessao.registrarHistorico();
      sessao.iniciarNovoJogo(Boolean.TRUE.equals(dados.isFirstPick()));
      draftSessaoRepository.salvar(sessao);

      return montarResposta(sessao);
    });
  }

  public Object desfazer(DraftSugestaoDto dados) {
    return comTrava(dados.sessionId(), () -> {
      DraftSessao sessao = buscarSessao(dados.sessionId());
      sessao.desfazer();
      draftSessaoRepository.salvar(sessao);
      return montarResposta(sessao);
    });
  }

  public Object refazer(DraftSugestaoDto dados) {
    return comTrava(dados.sessionId(), () -> {
      DraftSessao sessao = buscarSessao(dados.sessionId());
      sessao.refazer();
      draftSessaoRepository.salvar(sessao);
      return montarResposta(sessao);
    });
  }

  public Object acessarSessao(DraftSugestaoDto dados) {
    return montarResposta(buscarSessao(dados.sessionId()));
  }

  public Object obterSugestao(DraftSugestaoDto dados) {
    DraftSessao sessao = buscarSessao(dados.sessionId());
    if (sessao.getFaseAtual() == Fase.FIM) {
      return Map.of("champion", List.of());
    }
    if (sessao.registrarSugestao() > limiteSugestoesPorSessao) {
      throw new LimiteExcedidoException("Limite de sugestões desta sessão atingido");
    }
    String jogadorAtual = calcularJogadorAtual(sessao);
    boolean isBan = sessao.getFaseAtual().name().startsWith("BAN");
    SugestaoResponseDto resposta = pythonClient.pedirSugestao(montarRequest(sessao, jogadorAtual));
    return Map.of("champion", resposta.champion(), 
      "tipo", isBan ? "BAN" : "PICK",
      "jogador", jogadorAtual
    );
  }

  private <T> T comTrava(String sessionId, Supplier<T> acao) {
    if (sessoesOcupadas.putIfAbsent(sessionId, true) != null) {
      throw new AcaoEmAndamentoException("Ação já em andamento para essa sessão");
    }
    try {
      return acao.get();
    } finally {
      sessoesOcupadas.remove(sessionId);
    }
  }

  private DraftSessao buscarSessao(String sessionId) {
    DraftSessao sessao = draftSessaoRepository.buscar(sessionId);
    if (sessao == null) {
      throw new IllegalArgumentException("Sessão não encontrada");
    }
    return sessao;
  }

  private void aplicarAcao(DraftSessao sessao, String jogador, boolean isBan, String champion) {
    if (jogador.equals("PLAYER")) {
      if (isBan) {
        sessao.adicionarBanUser(champion);
      } else {
        sessao.adicionarPickUser(champion);
        sessao.adicionarFearless(champion);
      }
    } else {
      if (isBan) {
        sessao.adicionarBanIA(champion);
      } else {
        sessao.adicionarPickIA(champion);
        sessao.adicionarFearless(champion);
      }
    }
  }

  private DraftSugestaoRequestDto montarRequest(DraftSessao sessao, String jogadorAtual) {
    return new DraftSugestaoRequestDto(
      sessao.getLiga(), sessao.getTimeUser(), sessao.getBansUser(), sessao.getPicksUser(),
      sessao.getTimeIA(), sessao.getBansIA(), sessao.getPicksIA(),
      sessao.getFearless(), sessao.isFirstPick(),
      sessao.getFaseAtual().name(), jogadorAtual
    );
  }

  private String primeiroCampeao(Object champion) {
    if (champion instanceof List<?> lista) {
      if (lista.isEmpty()) {
        throw new IllegalStateException("A IA não retornou nenhuma sugestão");
      }
      return String.valueOf(lista.get(0));
    }
    return String.valueOf(champion);
  }

  private String calcularJogadorAtual(DraftSessao sessao) {
    Fase fase = sessao.getFaseAtual();
    if (fase == Fase.FIM) {
      return "FIM";
    }
    return (fase.getIsFirstPick() == sessao.isFirstPick()) ? "PLAYER" : "IA";
  }

  private boolean temMaisJogos(DraftSessao sessao) {
    return !(sessao.getGameAtual() == sessao.getTotalJogos() && sessao.getFaseAtual() == Fase.FIM);
  }

  private Map<String, Object> montarResposta(DraftSessao sessao) {
    Map<String, Object> resposta = new LinkedHashMap<>();
    resposta.put("sessionId", sessao.getSessionId());
    resposta.put("faseAtual", sessao.getFaseAtual().name());
    resposta.put("jogadorAtual", calcularJogadorAtual(sessao));
    resposta.put("gameAtual", sessao.getGameAtual());
    resposta.put("bansPlayer", sessao.getBansUser());
    resposta.put("bansIA", sessao.getBansIA());
    resposta.put("picksPlayer", sessao.getPicksUser());
    resposta.put("picksIA", sessao.getPicksIA());
    resposta.put("fearless", sessao.getFearless());
    resposta.put("temMaisJogos", temMaisJogos(sessao));
    resposta.put("podeDesfazer", sessao.podeDesfazer());
    resposta.put("podeRefazer", sessao.podeRefazer());
    return resposta;
  }

  public List<String> listarTimesPorLiga(String liga){
    return pythonClient.listarTimes(liga);
  }
}
