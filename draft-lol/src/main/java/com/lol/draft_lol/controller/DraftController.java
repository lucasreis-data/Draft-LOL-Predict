package com.lol.draft_lol.controller;

import java.util.List;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.lol.draft_lol.DTO.DraftAcaoDto;
import com.lol.draft_lol.DTO.DraftProxJogoDto;
import com.lol.draft_lol.DTO.DraftRequestDto;
import com.lol.draft_lol.DTO.DraftStartDto;
import com.lol.draft_lol.DTO.DraftSugestaoDto;
import com.lol.draft_lol.client.PythonDraftClient;
import com.lol.draft_lol.exception.AcaoEmAndamentoException;
import com.lol.draft_lol.service.ChampionService;
import com.lol.draft_lol.service.DraftService;
import com.lol.draft_lol.service.IpCliente;
import com.lol.draft_lol.service.TimeService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;


@RestController
public class DraftController {
  @Autowired
  private PythonDraftClient pythonClient;
  
  @Autowired
  private DraftService draftService;

   @Autowired
  private ChampionService championService;

  @Autowired
  private TimeService timeService;

  @Autowired
  private IpCliente ipCliente;

  @GetMapping("/Testar") 
  public String status(){
    return "Funcionou";
  }

  @GetMapping("/Python")
  public Object testar(){
    return pythonClient.obterStatusHome();
  }

  @GetMapping("/Ligas")
  public Object ligas(){
    return pythonClient.listarLigas();
  }

  @GetMapping("/Times")
  public List<String> listarTimes(@RequestParam(value = "liga", defaultValue = "LCK") String liga){
    return draftService.listarTimesPorLiga(liga);
  }

  @GetMapping("/draft/champions")
  public List<String> listarTodosChamps(){
    return championService.getCampeoes();
  }
   @GetMapping("/draft/times")
  public List<String> listarTodosTimes(@RequestParam(value = "liga", required = false) String liga){
    return draftService.listarTimesPorLiga(liga);
  }

  @GetMapping("/draft/Sugestao")
  public Object sugerir(@Valid DraftSugestaoDto request) {
    try {
      return ResponseEntity.ok(draftService.obterSugestao(request));
    } catch (IllegalArgumentException e) {
      return ResponseEntity.badRequest().body(e.getMessage());
    }
  }
  
  @GetMapping("/draft/sessao")
  public ResponseEntity<Object> acessarSessao(@Valid DraftSugestaoDto request) {
    try {
      return ResponseEntity.ok(draftService.acessarSessao(request));
    } catch (IllegalArgumentException e) {
      return ResponseEntity.badRequest().body(e.getMessage());
    }
  }

  @GetMapping("/draft/ligas/disponiveis")
  public Object ligasDisponiveis(){
    return pythonClient.listarLigasDisponiveis();
  }

  @PostMapping("/draft/Start")
  public ResponseEntity<Object> draftInicio(@RequestBody @Valid DraftStartDto request, HttpServletRequest http) {
    try {
      return ResponseEntity.ok(draftService.criarDraft(request, ipCliente.resolver(http)));
    } catch (IllegalArgumentException e) {
      return ResponseEntity.badRequest().body(e.getMessage());
    }
  }
  @PostMapping("/draft/Reiniciar-jogo")
  public ResponseEntity<Object> reiniciarJogo(@RequestBody @Valid DraftSugestaoDto request) {
    try {
      return ResponseEntity.ok(draftService.reiniciarJogo(request));
    } catch (AcaoEmAndamentoException e) {
      return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
    } catch (IllegalArgumentException e) {
      return ResponseEntity.badRequest().body(e.getMessage());
    }
  }

  @PostMapping("/draft/Prox-jogo")
public ResponseEntity<Object> proxJogo(@RequestBody @Valid DraftProxJogoDto request) {
  try {
    return ResponseEntity.ok(draftService.proxJogo(request));
  } catch (AcaoEmAndamentoException e) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
  } catch (IllegalArgumentException e) {
    return ResponseEntity.badRequest().body(e.getMessage());
  }
}

@PostMapping("/draft/desfazer")
public ResponseEntity<Object> desfazer(@RequestBody @Valid DraftSugestaoDto request) {
  try {
    return ResponseEntity.ok(draftService.desfazer(request));
  } catch (AcaoEmAndamentoException e) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
  } catch (IllegalArgumentException e) {
    return ResponseEntity.badRequest().body(e.getMessage());
  }
}

@PostMapping("/draft/refazer")
public ResponseEntity<Object> refazer(@RequestBody @Valid DraftSugestaoDto request) {
  try {
    return ResponseEntity.ok(draftService.refazer(request));
  } catch (AcaoEmAndamentoException e) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
  } catch (IllegalArgumentException e) {
    return ResponseEntity.badRequest().body(e.getMessage());
  }
}
@PostMapping("/draft/Picks-Bans")
public ResponseEntity<Object> alterarDraft(@RequestBody @Valid DraftAcaoDto request) {
  try {
    return ResponseEntity.ok(draftService.alterarDraft(request));
  } catch (AcaoEmAndamentoException e) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(e.getMessage());
  } catch (IllegalArgumentException e) {
    return ResponseEntity.badRequest().body(e.getMessage());
  }
}
}