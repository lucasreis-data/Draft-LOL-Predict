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
public class TimeService {
  
  @Autowired
  private PythonDraftClient pythonClient;

   private List<String> times;
 // private Set<String> times = new HashSet<>();

  public List<String> getTimes() {
    return times;
  }

  @PostConstruct
  public void carregarTimes(){
    this.times = pythonClient.listarTimes();
    //List<String> lista = pythonClient.listarTimes();
   // this.times = lista.stream().map(this::normalizar).collect(Collectors.toSet());
    
  }

  public boolean existe(String time){
    return this.times.stream()
        .anyMatch(t -> t.equalsIgnoreCase(time));
  }

  public String normalizar(String time){
    return this.times.stream()
        .filter(t -> t.equalsIgnoreCase(time))
        .findFirst()
        .orElse(time);
  }
}
