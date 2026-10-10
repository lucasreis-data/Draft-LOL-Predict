package com.lol.draft_lol.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import feign.FeignException;

@RestControllerAdvice
public class TratadorDeErros {

  private static final Logger log = LoggerFactory.getLogger(TratadorDeErros.class);

  @ExceptionHandler(LimiteExcedidoException.class)
  public ResponseEntity<Object> limite(LimiteExcedidoException e) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
  }

  /** Falha ao falar com o Python (ja depois das tentativas do retry). */
  @ExceptionHandler(FeignException.class)
  public ResponseEntity<Object> python(FeignException e) {
    log.warn("Falha na chamada ao Python: status={} msg={}", e.status(), e.getMessage());
    HttpStatus status = HttpStatus.resolve(e.status());
    if (status != null && status.is4xxClientError()) {
      return ResponseEntity.status(status).body("Requisição recusada pelo serviço de IA");
    }
    return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
        .body("Serviço de IA indisponível no momento. Tente novamente.");
  }
}
