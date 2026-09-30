package com.lol.draft_lol.model;

public enum Fase {
  BAN_1(Boolean.TRUE),
  BAN_2(Boolean.FALSE),
  BAN_3(Boolean.TRUE),
  BAN_4(Boolean.FALSE),
  BAN_5(Boolean.TRUE),
  BAN_6(Boolean.FALSE),

  PICK_1(Boolean.TRUE),
  PICK_2(Boolean.FALSE),
  PICK_3(Boolean.FALSE),
  PICK_4(Boolean.TRUE),
  PICK_5(Boolean.TRUE),
  PICK_6(Boolean.FALSE),

  BAN_7(Boolean.FALSE),
  BAN_8(Boolean.TRUE),
  BAN_9(Boolean.FALSE),
  BAN_10(Boolean.TRUE),

  PICK_7(Boolean.FALSE),
  PICK_8(Boolean.TRUE),
  PICK_9(Boolean.TRUE),
  PICK_10(Boolean.FALSE),

  FIM(null);

  private final Boolean isFirstPick;

  Fase(Boolean isFirstPick){
    this.isFirstPick = isFirstPick;
  }

  public Boolean getIsFirstPick(){
    return isFirstPick;
  }

  public ResultadoFase proximaFase(boolean isFirstPick){
    if(this == FIM){
      return new ResultadoFase(FIM, "FIM");

    }
    int proximoIndice = this.ordinal() + 1;
    Fase proxima = Fase.values()[proximoIndice];

    if(proxima == FIM){
      return new ResultadoFase(FIM, "FIM");
    }

    String jogadorAtual = (proxima.isFirstPick == isFirstPick)? "PLAYER" : "IA";
    return new ResultadoFase(proxima, jogadorAtual);
  }

  public record ResultadoFase(Fase fase, String jogador){}
} 