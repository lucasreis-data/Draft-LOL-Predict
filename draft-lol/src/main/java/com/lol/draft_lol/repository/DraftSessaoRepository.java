package com.lol.draft_lol.repository;

import java.time.Duration;

import com.lol.draft_lol.model.DraftSessao;

public interface DraftSessaoRepository {
  DraftSessao buscar(String sessionId);
  void salvar(DraftSessao sessao);

  /** Cria a sessao se o IP dela ainda nao atingiu o limite. Atomico. Devolve false se recusou. */
  boolean criar(DraftSessao sessao, int maxSessoesPorIp);

  /** Remove sessoes sem acesso ha mais que a duracao dada. Devolve quantas removeu. */
  int removerInativas(Duration inatividade);

  int total();
}
