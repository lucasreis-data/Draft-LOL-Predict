package com.lol.draft_lol.repository;

import com.lol.draft_lol.model.DraftSessao;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class DraftSessaoRepositoryMemoria implements DraftSessaoRepository {

  private final Map<String, DraftSessao> sessoes = new ConcurrentHashMap<>();

  @Override
  public DraftSessao buscar(String sessionId) {
    return sessoes.get(sessionId);
  }

  @Override
  public void salvar(DraftSessao sessao) {
    sessoes.put(sessao.getSessionId(), sessao);
  }
}