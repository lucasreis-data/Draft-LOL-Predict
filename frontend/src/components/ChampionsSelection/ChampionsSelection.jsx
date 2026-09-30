import React from 'react';

const ChampionsSelection = ({
  ligaEscolhido,
  setLigaEscolhida,
  ligaDisponiveis,
  formatoMD,
  setFormatoMD,
  timeConfirmadoBlue,
  timeConfirmadoRed,
  iniciarDraft,
  timeDaVez,
  buscarChamp,
  setBuscarChamp,
  confirmarSelecao,
  pickBanChamp,
  botaoDesabilitado,
  textoBotao,
  pickBanChampIA,
  nextJogo,
  champsFiltrados,
  champsBloqueados,
  selecaoTemporaria,
  sugestaoIA,
  tratarCliqueNoChamp
}) => {
  return (
    <main className='champions-selection main-content'>
      <header className="filter-header draft-settings-header">
        <select 
          className='league-select'
          value={ligaEscolhido} 
          onChange={(e) => setLigaEscolhida(e.target.value)}
        >
          {ligaDisponiveis.map((liga) =>(
            <option key={liga} value={liga} className='league-option'>
              {liga}
            </option>
          ))}
        </select>
        <label className='md-format-label'>
          <input 
            type="checkbox" 
            className='md-format-checkbox'
            checked={formatoMD === 1}
            onChange={() => setFormatoMD(1)} 
          /> MD1
        </label>
        <label className='md-format-label'>
          <input 
            type="checkbox" 
            className='md-format-checkbox'
            checked={formatoMD === 3}
            onChange={() => setFormatoMD(3)} 
          /> MD3
        </label>
        <label className='md-format-label'>
          <input 
            type="checkbox" 
            className='md-format-checkbox'
            checked={formatoMD === 5}
            onChange={() => setFormatoMD(5)} 
          /> MD5
        </label>
        {(timeConfirmadoBlue !== null && timeConfirmadoRed !== null && timeConfirmadoBlue.name !== timeConfirmadoRed.name) && (
          <button 
            className='bn-iniciar-draft start-draft-button'
            onClick={iniciarDraft}
          >
            iniciarDraft
          </button>
        )}

        <h3 className='turn-indicator-title'>{timeDaVez}</h3>
      </header>
      
      <p className='fearless-bans-text'>champs banidos pelo fearless</p>
      <h2 className='picks-bans-title'>Picks e Bans</h2>
      
      <header className='search-header champ-search-header'>
        <input 
          className='search-input champ-search-input'
          value={buscarChamp}
          onChange={(e) => setBuscarChamp(e.target.value)}
          type="text" 
          placeholder='Pesquisar campeao...' 
        />
        <div className='confirm-area confirm-selection-area'>
          <button
            className='btn-confirmar confirm-champ-button'
            onClick={() => {
              confirmarSelecao();
              pickBanChamp();
            }}
            disabled={botaoDesabilitado}
          >
            {textoBotao}
          </button>
        </div>
        <div className='confirm-area ia-play-area'>
          <button 
            className='btn-jogar-ia ia-play-button'
            onClick={pickBanChampIA}
          >
            IA joga
          </button>
        </div>
        <div className='prox-jogo next-game-area'>
          <button 
            className='btn-prox-jogo next-game-button'
            onClick={nextJogo}
          >
            PROX JOGO
          </button>
        </div>
      </header>
      
      <header className="filter-header position-filter-header">
        <input type="checkbox" id="top" name="position" className='position-checkbox' />Top
        <input type="checkbox" id="Jungle" name="position" className='position-checkbox' />Jungle
        <input type="checkbox" id="Mid" name="position" className='position-checkbox' />Mid
        <input type="checkbox" id="Adc" name="position" className='position-checkbox' />Adc
        <input type="checkbox" id="Sup" name="position" className='position-checkbox' />Sup
      </header>

      <p className='champ-list-text'>lista de champs</p>
      <div className='champions-grid champ-grid-container'>
        {champsFiltrados.map((champion) => {
          const foiConfirmado = champsBloqueados.includes(champion.name)
          let estaSelecionadoAgora = selecaoTemporaria?.name === champion.name
          const isSugestaoIA = sugestaoIA.includes(champion.name)
          let nivelSugestaoIA = " 0"

          if(sugestaoIA[0] === champion.name){
            nivelSugestaoIA = "nivel-1"
          } else if(sugestaoIA[1] === champion.name){
            nivelSugestaoIA = "nivel-2"
          } else if(sugestaoIA[2] === champion.name){
            nivelSugestaoIA = "nivel-3"
          }

          let classeFinal = "champion-card champ-card-item"
          if(foiConfirmado){
            classeFinal += " disabled"
          } else if(estaSelecionadoAgora){
            classeFinal += " selected"
          } else if(isSugestaoIA){
            classeFinal += " suggested " + nivelSugestaoIA
          }
          const clicarNoChamp = () => {
            if(!foiConfirmado){
              tratarCliqueNoChamp(champion)
            }
          }
          return (
            <div
              key={champion.name}
              className={classeFinal}
              onClick={clicarNoChamp}
            >
              {champion.name}
            </div>
          )
        })}
      </div>
    </main>
  );
};

export default ChampionsSelection;
