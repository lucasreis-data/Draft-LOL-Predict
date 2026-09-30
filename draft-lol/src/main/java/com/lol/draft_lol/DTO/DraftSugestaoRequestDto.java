package com.lol.draft_lol.DTO;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

public record DraftSugestaoRequestDto(
  @JsonProperty("liga") String liga,
  @JsonProperty("time_player") String timePlayer,
  @JsonProperty("bans_player") List<String> bansPlayer,
  @JsonProperty("picks_player") List<String> picksPlayer,
  @JsonProperty("time_ia") String timeIA,
  @JsonProperty("bans_ia") List<String> bansIA,
  @JsonProperty("picks_ia") List<String> picksIA,
  @JsonProperty("fearless") List<String> fearless,
  @JsonProperty("is_first_pick") boolean isFirstPick,
  @JsonProperty("fase") String fase,
  @JsonProperty("jogador_atual") String jogadorAtual
) {}