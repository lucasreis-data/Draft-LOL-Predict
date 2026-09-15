package com.lol.draft_lol.service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.lol.draft_lol.DTO.DraftAcaoDto;
import com.lol.draft_lol.DTO.DraftProxJogoDto;
import com.lol.draft_lol.DTO.DraftRequestDto;
import com.lol.draft_lol.DTO.DraftStartDto;
import com.lol.draft_lol.client.PythonDraftClient;
import com.lol.draft_lol.exception.AcaoEmAndamentoException;

import feign.FeignException;

@Service
public class DraftService {
  
  @Autowired
  private PythonDraftClient pythonClient;
  @Autowired
  private TimeService timeService;
  @Autowired
  private ChampionService championService;

  private final Map<String, Boolean> sessoesOcupadas = new ConcurrentHashMap<>();

  public Object gerarDraft(DraftRequestDto dados){
    if (!timeService.existe(dados.timeA())) {
        throw new IllegalArgumentException("Time não encontrado: " + dados.timeA());
    }
    if (!timeService.existe(dados.timeB())) {
        throw new IllegalArgumentException("Time não encontrado: " + dados.timeB());
    }
    String timeA = timeService.normalizar(dados.timeA());
    String timeB = timeService.normalizar(dados.timeB());
    DraftRequestDto dadosNormalizados = new DraftRequestDto(
      timeA, 
      timeB, 
      dados.quantidadeJogos()
    );

    return pythonClient.preverDraft(dados);
  }

  public Object criarDraft(DraftStartDto dados){
    if(!timeService.existe(dados.timeIA())){
      throw new IllegalArgumentException("Time não encontrado: " + dados.timeIA());
    }
    if(!timeService.existe(dados.timeUsuario())){
      throw new IllegalArgumentException("Time não encontrado: " + dados.timeUsuario());
    }
    String timeIA = timeService.normalizar(dados.timeIA());
    String timeUsuario = timeService.normalizar(dados.timeUsuario());
    DraftStartDto dadosNormalizados = new DraftStartDto(
      timeIA, 
      timeUsuario, 
      dados.quantidadeJogos(),
      dados.isFirstPick(),
      dados.liga()
    );
    return pythonClient.iniciarDraft(dados);
  }

  public Object alterarDraft(DraftAcaoDto dados){
    String sessionId = dados.sessionId();
    if (sessoesOcupadas.putIfAbsent(sessionId, true) != null) {
      throw new AcaoEmAndamentoException("Ação já em andamento para essa sessão");
    }
    try{
      DraftAcaoDto dadosParaEnviar = dados;
      if(dados.champion() != null){
        if(!championService.existe(dados.champion())){
          throw new IllegalArgumentException("Campeão não encontrado: " + dados.champion());
        }
      String campeao = championService.normalizar(dados.champion());
      dadosParaEnviar = new DraftAcaoDto(dados.sessionId(), campeao);
      }

    try {
        return pythonClient.alterarDraft(dados);
    } catch (FeignException.NotFound e) {
      throw new IllegalArgumentException("Sessão não encontrada");
    }
  } finally{
    sessoesOcupadas.remove(sessionId);
  }
  }

  public Object proxJogo(DraftProxJogoDto dados){
    try {
        return pythonClient.proxJogo(dados);
    } catch (FeignException.NotFound e) {
      throw new IllegalArgumentException("Sessão não encontrada");
    }
  }
}
