package com.lol.draft_lol.service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.lol.draft_lol.client.PythonDraftClient;

import jakarta.annotation.PostConstruct;

@Service
public class ChampionService {

  @Autowired
  private PythonDraftClient pythonClient;

  private List<String> campeoes;
  // private Set<String> campeoes = new HashSet<>();

  public List<String> getCampeoes() {
    return this.campeoes;
  }

  @PostConstruct
  public void carregarCampeoes(){
    this.campeoes = pythonClient.listarCampeoes();
    // List<String> lista = pythonClient.listarCampeoes();
    // this.campeoes = lista.stream().map(this::normalizar).collect(Collectors.toSet());
  }

  public boolean existe(String campeao){
    return this.campeoes.stream()
        .anyMatch(c -> c.equalsIgnoreCase(campeao));
  }

  public String normalizar(String campeao){
    return this.campeoes.stream()
        .filter(c -> c.equalsIgnoreCase(campeao))
        .findFirst()
        .orElse(campeao);
  }
}
