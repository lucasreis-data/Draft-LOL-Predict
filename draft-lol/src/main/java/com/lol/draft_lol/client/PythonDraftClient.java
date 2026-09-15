package com.lol.draft_lol.client;

import java.util.List;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.lol.draft_lol.DTO.DraftAcaoDto;
import com.lol.draft_lol.DTO.DraftProxJogoDto;
import com.lol.draft_lol.DTO.DraftRequestDto;
import com.lol.draft_lol.DTO.DraftStartDto;

import io.swagger.v3.oas.annotations.parameters.RequestBody;

@FeignClient(name="python-ai", url = "http://localhost:5000")
public interface PythonDraftClient {

  @GetMapping("/")
  Object obterStatusHome();

  @GetMapping("/ligas")
  Object listarLigas();

  @GetMapping("/times")
  List<String> listarTimes();

  @GetMapping("/campeoes")
  List<String> listarCampeoes();

  @GetMapping("/draft/sugestao")
  Object pedirSugestao(@RequestParam("sessionId") String sessionId);

  @GetMapping("/acessar-sessao")
  Object acessarSessao(@RequestParam("sessionId") String sessionId);

  @GetMapping("/ligas/disponiveis")
  Object listarLigasDisponiveis();
  
  @PostMapping("/predict")
  Object preverDraft(@RequestBody DraftRequestDto dados);

  @PostMapping("/draft/iniciar")
  Object iniciarDraft(@RequestBody DraftStartDto dados);

  @PostMapping("/draft/acao")
  Object alterarDraft(@RequestBody DraftAcaoDto dados);

  @PostMapping("/draft/novo-jogo")
  Object proxJogo(@RequestBody DraftProxJogoDto dados);

}
