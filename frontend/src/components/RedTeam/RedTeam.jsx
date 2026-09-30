import React from 'react';

const RedTeam = ({
  timeConfirmadoRed,
  timeConfirmadoBlue,
  times,
  timeTempRed,
  setTimeTempRed,
  confirmarTimeRed,
  ladoFirstPick,
  setLadoFirstPick,
  dadosDraftJava
}) => {
  return (
    <aside className='red-team red-team-container'>
      <h2 className='team-title red-team-title'> {timeConfirmadoRed ? timeConfirmadoRed.name : "Red Side"} </h2>
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
                if(timeTempRed != null && timeTempRed.name === time.name){
                  classeTime += " selected-red"
                }
                return (
                  <div
                    key={time.name}
                    className={classeTime}
                    onClick={() => setTimeTempRed(time)}>
                    {time.name}
                  </div>
                )
              })}
            </div>

            <button
              className='btn-confirmar-time team-confirm-button'
              onClick={confirmarTimeRed}
              disabled={timeTempRed === null}  
            >
              Confirmar time vermelho
            </button>
          </div>
        )}
      </header>
      
      <header className="filter-header first-pick-header">
        <label className='first-pick-label'>
          <input 
            type="checkbox" 
            className='first-pick-checkbox'
            checked={ladoFirstPick === 'RED'}
            onChange={() => setLadoFirstPick('RED')}
          /> é first pick?
        </label>
      </header>
      
      <div className='bans bans-container'>
        <h3 className='bans-title'>Bans IA</h3>
        {dadosDraftJava?.bansIA?.map((nomeChamp, index) => (
          <div key={index} className='ban-item ban-item-ia'> {nomeChamp}</div>
        ))}
      </div>
      
      <div className='picks picks-container'>
        <h3 className='picks-title'>Picks IA</h3>
        {dadosDraftJava?.picksIA?.map((nomeChamp, index) => (
          <div key={index} className='pick-item pick-item-ia'> {nomeChamp}</div>
        ))}
      </div>
    </aside>
  );
};

export default RedTeam;
