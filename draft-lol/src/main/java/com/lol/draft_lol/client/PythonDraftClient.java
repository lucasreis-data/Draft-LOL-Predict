package com.lol.draft_lol.client;

import java.util.List;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;

import com.lol.draft_lol.DTO.DraftRequestDto;
import com.lol.draft_lol.DTO.DraftSugestaoRequestDto;
import com.lol.draft_lol.DTO.SugestaoResponseDto;

@FeignClient(name = "python-ai", url = "http://localhost:5000")
public interface PythonDraftClient {

  @GetMapping("/")
  Object obterStatusHome();

  @GetMapping("/ligas")
  Object listarLigas();

  @GetMapping("/times")
  List<String> listarTimes();

  @GetMapping("/times")
  List<String> listarTimes(@RequestParam("ligas") String liga);

  @GetMapping("/campeoes")
  List<String> listarCampeoes();

  @GetMapping("/ligas/disponiveis")
  Object listarLigasDisponiveis();

  @PostMapping("/predict")
  Object preverDraft(@RequestBody DraftRequestDto dados);

  @PostMapping("/draft/sugestao")
  SugestaoResponseDto pedirSugestao(@RequestBody DraftSugestaoRequestDto dados);

  @PostMapping("/draft/acao")
  SugestaoResponseDto pedirAcao(@RequestBody DraftSugestaoRequestDto dados);
  
}