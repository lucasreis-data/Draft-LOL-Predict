package com.lol.draft_lol.repository;

import com.lol.draft_lol.model.DraftSessao;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class DraftSessaoRepositoryMemoria implements DraftSessaoRepository {

  private final Map<String, DraftSessao> sessoes = new ConcurrentHashMap<>();
  private final Object travaCriacao = new Object();

  @Override
  public DraftSessao buscar(String sessionId) {
    DraftSessao sessao = sessoes.get(sessionId);
    if (sessao != null) {
      sessao.tocar();
    }
    return sessao;
  }

  @Override
  public void salvar(DraftSessao sessao) {
    sessao.tocar();
    sessoes.put(sessao.getSessionId(), sessao);
  }

  @Override
  public boolean criar(DraftSessao sessao, int maxSessoesPorIp) {
    // Contar e inserir precisam ser uma operacao so, senao duas requisicoes
    // simultaneas do mesmo IP passariam juntas pelo limite.
    synchronized (travaCriacao) {
      String ip = sessao.getIpOrigem();
      long doMesmoIp = sessoes.values().stream()
          .filter(s -> ip != null && ip.equals(s.getIpOrigem()))
          .count();
      if (doMesmoIp >= maxSessoesPorIp) {
        return false;
      }
      salvar(sessao);
      return true;
    }
  }

  @Override
  public int removerInativas(Duration inatividade) {
    Instant corte = Instant.now().minus(inatividade);
    int antes = sessoes.size();
    sessoes.values().removeIf(s -> s.getUltimoAcesso().isBefore(corte));
    return antes - sessoes.size();
  }

  @Override
  public int total() {
    return sessoes.size();
  }
}
