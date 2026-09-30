import React from 'react';

const BlueTeam = ({
  timeConfirmadoBlue,
  timeConfirmadoRed,
  times,
  timeTempBlue,
  setTimeTempBlue,
  confirmarTimeBlue,
  ladoFirstPick,
  setLadoFirstPick,
  dadosDraftJava
}) => {
  return (
    <aside className='blue-team blue-team-container'>
      <h2 className='team-title blue-team-title'>{timeConfirmadoBlue ? timeConfirmadoBlue.name : "Blue Side"}</h2>
      <header className='search-header team-search-header'>
        <input 
          type="text" 
          placeholder='Pesquisar time...' 
          className='search-input time-search-input'
        />
        
        {(timeConfirmadoBlue === null || timeConfirmadoRed === null || timeConfirmadoBlue.name === timeConfirmadoRed.name) && (
          <div className='selecao-time-container team-selection-container'>
            <div className='times-lista team-list'>
              {times.map((time) => {
                let classeTime = "time-card team-card-item"
                if (timeTempBlue != null && timeTempBlue.name === time.name) {
                  classeTime += " selected-blue"
                }
                return (
                  <div
                    key={time.name}
                    className={classeTime}
                    onClick={() => setTimeTempBlue(time)}>
                    {time.name}
                  </div>
                )
              })}
            </div>
            <button
              className='btn-confirmar-time team-confirm-button'
              onClick={confirmarTimeBlue}
              disabled={timeTempBlue === null}  
            >
              Confirmar time azul
            </button>
          </div>
        )}
      </header>
      
      <header className="filter-header first-pick-header">
        <label className='first-pick-label'>
          <input 
            type="checkbox" 
            className='first-pick-checkbox'
            checked={ladoFirstPick === 'BLUE'}
            onChange={() => setLadoFirstPick('BLUE')}
          /> é first pick?
        </label>
      </header>
      
      <div className='bans bans-container'>
        <h3 className='bans-title'>Seus Bans</h3>
        {dadosDraftJava?.bansPlayer?.map((nomeChamp, index) => (
          <div key={index} className='ban-item ban-item-player'> {nomeChamp}</div>
        ))}
      </div>
      
      <div className='picks picks-container'>
        <h3 className='picks-title'>Seus Picks</h3>
        {dadosDraftJava?.picksPlayer?.map((nomeChamp, index) => (
          <div key={index} className='pick-item pick-item-player'> {nomeChamp}</div>
        ))}
      </div>
    </aside>
  );
};

export default BlueTeam;
