package com.lol.draft_lol.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SugestaoResponseDto (
  @JsonProperty("champion") Object champion
){}
