package com.lol.draft_lol.model;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class DraftSessao {
  private String sessionId;
  private int totalJogos;
  private boolean isFirstPick;
  private String timeUser;
  private String timeIA;
  private String liga;
  private int gameAtual;
  private Fase faseAtual;
  private List<String> picksUser;
  private List<String> picksIA;
  private List<String> bansUser;
  private List<String> bansIA;
  private List<String> fearless;

  private final Deque<DraftSessao> historico = new ArrayDeque<>();
  private final Deque<DraftSessao> pilhaRefazer = new ArrayDeque<>();

  public DraftSessao(String sessionId, String timeUser, String timeIA, String liga, boolean isFirstPick, int totalJogos) {
    this.sessionId = sessionId;
    this.timeUser = timeUser;
    this.timeIA = timeIA;
    this.liga = liga;
    this.isFirstPick = isFirstPick;
    this.totalJogos = totalJogos;
    this.gameAtual = 1;
    this.faseAtual = Fase.BAN_1;
    this.picksUser = new ArrayList<>();
    this.picksIA = new ArrayList<>();
    this.bansUser = new ArrayList<>();
    this.bansIA = new ArrayList<>();
    this.fearless = new ArrayList<>();
  }

  public DraftSessao clonar() {
    DraftSessao copia = new DraftSessao(sessionId, timeUser, timeIA, liga, isFirstPick, totalJogos);
    copia.gameAtual = this.gameAtual;
    copia.faseAtual = this.faseAtual;
    copia.picksUser = new ArrayList<>(this.picksUser);
    copia.picksIA = new ArrayList<>(this.picksIA);
    copia.bansUser = new ArrayList<>(this.bansUser);
    copia.bansIA = new ArrayList<>(this.bansIA);
    copia.fearless = new ArrayList<>(this.fearless);
    return copia;
  }

  public boolean campeaoIndisponivel(String campeao) {
    return fearless.contains(campeao) || bansUser.contains(campeao) || bansIA.contains(campeao);
  }

  public void iniciarNovoJogo(boolean isFirstPick) {
    this.gameAtual++;
    this.isFirstPick = isFirstPick;
    this.faseAtual = Fase.BAN_1;
    this.picksUser = new ArrayList<>();
    this.picksIA = new ArrayList<>();
    this.bansUser = new ArrayList<>();
    this.bansIA = new ArrayList<>();
  }

  public void registrarHistorico() {
    historico.push(this.clonar());
    pilhaRefazer.clear(); 
  }

  public boolean podeDesfazer() {
    return !historico.isEmpty();
  }

  public boolean podeRefazer() {
    return !pilhaRefazer.isEmpty();
  }

  public void desfazer() {
    if (historico.isEmpty()) return;
    DraftSessao anterior = historico.pop();
    pilhaRefazer.push(this.clonar());
    restaurarDe(anterior);
  }

  public void refazer() {
    if (pilhaRefazer.isEmpty()) return;
    DraftSessao proximo = pilhaRefazer.pop();
    historico.push(this.clonar());
    restaurarDe(proximo);
  }

  private void restaurarDe(DraftSessao outra) {
    this.gameAtual = outra.gameAtual;
    this.faseAtual = outra.faseAtual;
    this.isFirstPick = outra.isFirstPick;
    this.picksUser = new ArrayList<>(outra.picksUser);
    this.picksIA = new ArrayList<>(outra.picksIA);
    this.bansUser = new ArrayList<>(outra.bansUser);
    this.bansIA = new ArrayList<>(outra.bansIA);
    this.fearless = new ArrayList<>(outra.fearless);
  }

  public String getSessionId() { return sessionId; }
  public int getTotalJogos() { return totalJogos; }
  public boolean isFirstPick() { return isFirstPick; }
  public String getTimeUser() { return timeUser; }
  public String getTimeIA() { return timeIA; }
  public String getLiga() { return liga; }
  public int getGameAtual() { return gameAtual; }
  public Fase getFaseAtual() { return faseAtual; }
  public void setFaseAtual(Fase faseAtual) { this.faseAtual = faseAtual; }

  public List<String> getPicksUser() { return picksUser; }
  public List<String> getPicksIA() { return picksIA; }
  public List<String> getBansUser() { return bansUser; }
  public List<String> getBansIA() { return bansIA; }
  public List<String> getFearless() { return fearless; }

  public void adicionarPickUser(String campeao) { this.picksUser.add(campeao); }
  public void adicionarPickIA(String campeao) { this.picksIA.add(campeao); }
  public void adicionarBanUser(String campeao) { this.bansUser.add(campeao); }
  public void adicionarBanIA(String campeao) { this.bansIA.add(campeao); }
  public void adicionarFearless(String campeao) { this.fearless.add(campeao); }
}