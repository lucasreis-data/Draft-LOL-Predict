package com.lol.draft_lol.repository;

import com.lol.draft_lol.model.DraftSessao;

public interface DraftSessaoRepository {
  DraftSessao buscar(String sessionId);
  void salvar(DraftSessao sessao);
}
