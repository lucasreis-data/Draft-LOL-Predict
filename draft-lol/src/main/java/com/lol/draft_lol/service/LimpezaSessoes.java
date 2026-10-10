package com.lol.draft_lol.service;

import java.time.Duration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.lol.draft_lol.repository.DraftSessaoRepository;

/** Apaga sessoes abandonadas. Como as sessoes ficam em memoria, sem isso o heap so cresce. */
@Component
public class LimpezaSessoes {

  private static final Logger log = LoggerFactory.getLogger(LimpezaSessoes.class);

  @Autowired
  private DraftSessaoRepository repositorio;

  @Value("${draft.limpeza.inatividade-ms:7200000}")
  private long inatividadeMs;

  // O primeiro disparo so ocorre apos um intervalo (nao ha o que limpar logo ao subir).
  @Scheduled(
      fixedDelayString = "${draft.limpeza.intervalo-ms:7200000}",
      initialDelayString = "${draft.limpeza.intervalo-ms:7200000}")
  public void limpar() {
    int removidas = repositorio.removerInativas(Duration.ofMillis(inatividadeMs));
    log.info("Limpeza de sessoes: {} removidas, {} restantes", removidas, repositorio.total());
  }
}
