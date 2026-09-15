package com.lol.draft_lol.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

public record DraftStartDto (

  @Schema(example = "LOUD", description= "Qual time você irá representar?")
  @NotBlank(message = "O time não pode estar vazio")
  @JsonProperty("timeUsuario")
  String timeUsuario,

  @Schema(example = "FURIA", description= "Qual time a IA irá representar?")
  @NotBlank(message = "O time não pode estar vazio")
  @JsonProperty("timeIA")
  String timeIA,

  @Schema(example = "3", description= "Quantidade de jogos na serie(apenas número)")
  @NotBlank(message = "A quantidade não pode estar vazio")
  @JsonProperty("quantidadeJogos")
  Integer quantidadeJogos,

  @Schema(example = "true", description= "Você vai ser First Pick? sim(true) ou não (false) ")
  @JsonProperty("isFirstPick")
  Boolean isFirstPick,

  @Schema(example = "CBLOL", description = "Qual liga usar para as sugestões da IA")
  @JsonProperty("liga")
  String liga

){}
