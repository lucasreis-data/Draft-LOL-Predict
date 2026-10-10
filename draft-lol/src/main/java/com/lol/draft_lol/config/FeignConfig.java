package com.lol.draft_lol.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import feign.RetryableException;
import feign.Retryer;
import feign.codec.ErrorDecoder;

/**
 * Retry das chamadas ao Python.
 *
 * Todas as rotas do Python so calculam (nao gravam nada), entao repetir e seguro.
 * Repete em: falha de rede/timeout (o Feign ja trata IOException como repetivel) e
 * em 502/503/504 (tarefa Python sendo trocada, Service Connect sem destino saudavel).
 * Erros 4xx e 500 NAO sao repetidos: repetir nao muda o resultado.
 *
 * Orcamento de tempo: o CloudFront corta em 30 s. Com read-timeout de 8 s e 3 tentativas,
 * o pior caso fica em ~25 s. Se aumentar o read-timeout, reduza as tentativas.
 */
@Configuration
public class FeignConfig {

  private static final int TENTATIVAS = 3;
  private static final long ESPERA_INICIAL_MS = 200;
  private static final long ESPERA_MAXIMA_MS = 1000;

  @Bean
  public Retryer feignRetryer() {
    return new Retryer.Default(ESPERA_INICIAL_MS, ESPERA_MAXIMA_MS, TENTATIVAS);
  }

  @Bean
  public ErrorDecoder feignErrorDecoder() {
    ErrorDecoder padrao = new ErrorDecoder.Default();
    return (metodo, resposta) -> {
      Exception erro = padrao.decode(metodo, resposta);
      int status = resposta.status();
      if ((status == 502 || status == 503 || status == 504) && !(erro instanceof RetryableException)) {
        return new RetryableException(
            status, erro.getMessage(), resposta.request().httpMethod(), erro, (Long) null, resposta.request());
      }
      return erro;
    };
  }
}
