import React, { useState, useEffect } from 'react';
import { useSeries } from './hooks/useSeries';
import { useDraft } from './hooks/useDraft';

import ConfigModal from './components/Modals/ConfigModal';
import FirstPickModal from './components/Modals/FirstPickModal';
import EndSeriesModal from './components/Modals/EndSeriesModal';
import BottomBar from './components/BottomBar/BottomBar';
import TeamPanel from './components/Panels/TeamPanel';
import ChampionGrid from './components/ChampionGrid/ChampionGrid';
import HistoryDrawer from './components/Drawers/HistoryDrawer';

import './App.css';

const DRAFT_ORDER = [
  {type:'ban', side:'fp'}, {type:'ban', side:'lp'}, {type:'ban', side:'fp'}, {type:'ban', side:'lp'}, {type:'ban', side:'fp'}, {type:'ban', side:'lp'},
  {type:'pick', side:'fp'}, {type:'pick', side:'lp'}, {type:'pick', side:'lp'}, {type:'pick', side:'fp'}, {type:'pick', side:'fp'}, {type:'pick', side:'lp'},
  {type:'ban', side:'lp'}, {type:'ban', side:'fp'}, {type:'ban', side:'lp'}, {type:'ban', side:'fp'},
  {type:'pick', side:'lp'}, {type:'pick', side:'fp'}, {type:'pick', side:'fp'}, {type:'pick', side:'lp'},
];

export default function App() {
  const series = useSeries();
  const draft = useDraft(series);

  const [searchQuery, setSearchQuery] = useState('');
  const [suggestionsOn, setSuggestionsOn] = useState(true);
  const [historyPanelOpen, setHistoryPanelOpen] = useState(false);
  const [activeRole, setActiveRole] = useState(null);

  const stepIndex = (draft.dadosDraft?.bansPlayer?.length || 0) + 
                    (draft.dadosDraft?.bansIA?.length || 0) + 
                    (draft.dadosDraft?.picksPlayer?.length || 0) + 
                    (draft.dadosDraft?.picksIA?.length || 0);

  const draftAcabou = stepIndex >= DRAFT_ORDER.length;
  const isPlayerFP = series.teamOnSide[series.ladoFirstPick]?.key === series.time1?.key;
  
  let activeSide = null;
  if (!draftAcabou) {
    const step = DRAFT_ORDER[stepIndex];
    if (step.side === 'fp') {
      activeSide = series.ladoFirstPick;
    } else {
      activeSide = series.ladoFirstPick === 'blue' ? 'red' : 'blue';
    }
  }

  const bansPlayer = draft.dadosDraft?.bansPlayer || [];
  const bansIA = draft.dadosDraft?.bansIA || [];
  const picksPlayer = draft.dadosDraft?.picksPlayer || [];
  const picksIA = draft.dadosDraft?.picksIA || [];

  const playerSide = isPlayerFP ? series.ladoFirstPick : (series.ladoFirstPick === 'blue' ? 'red' : 'blue');
  const iaSide = playerSide === 'blue' ? 'red' : 'blue';

  const bansBySide = {
    [playerSide]: bansPlayer,
    [iaSide]: bansIA
  };
  
  const picksBySide = {
    [playerSide]: picksPlayer,
    [iaSide]: picksIA
  };

  const fearless = draft.dadosDraft?.fearless || [];
  const allBanned = [...bansPlayer, ...bansIA, ...picksPlayer, ...picksIA, ...fearless];

  const handleConfigConfirm = (t1, t2, f, lig) => {
    series.finishConfig(t1, t2, f, lig);
  };

  const handleStartGameConfirm = (side, isFpTime1) => {
    series.startNextGame(side, isFpTime1);
    draft.iniciarJogo(isFpTime1);
  };

  const handleNextGameAction = () => {
    series.finishGame({
      fpName: series.teamOnSide[series.ladoFirstPick]?.name,
      lpName: series.teamOnSide[series.ladoFirstPick === 'blue' ? 'red' : 'blue']?.name,
      picksFp: picksBySide[series.ladoFirstPick],
      picksLp: picksBySide[series.ladoFirstPick === 'blue' ? 'red' : 'blue']
    });
    series.nextGameModal();
  };

  const actionLabel = () => {
    if (draftAcabou) return 'Draft concluído';
    const step = DRAFT_ORDER[stepIndex];
    const soFar = DRAFT_ORDER.slice(0, stepIndex + 1).filter(s => s.type === step.type && s.side === step.side).length;
    const team = series.teamOnSide[activeSide];
    return `${step.type === 'ban' ? 'Ban' : 'Pick'} ${soFar} — ${team?.name || ''}`;
  };

  const isPlayerTurn = draft.jogadorAtual === 'PLAYER';

  return (
    <div className="shell">
      <ConfigModal 
        show={series.showConfigModal} 
        ligas={draft.ligasDisponiveis} 
        onConfirm={handleConfigConfirm} 
      />
      
      <FirstPickModal 
        show={series.showStartModal} 
        gameNum={series.jogoAtual} 
        time1={series.time1} 
        time2={series.time2} 
        onConfirm={handleStartGameConfirm} 
      />
      
      <EndSeriesModal 
        show={series.showEndModal} 
        onHistory={() => { series.setShowEndModal(false); setHistoryPanelOpen(true); }} 
        onRestart={() => { series.resetSeries(); }} 
      />

      {/* ---- BARRA DE NAVEGAÇÃO DO JOGO ---- */}
      <div className="gamenav">
        {/* Esquerda: Liga e formato */}
        <div className="gamenav-left">
          <span className="gamenav-liga">{series.liga}</span>
          <span className="gamenav-sep">|</span>
          <span className="gamenav-formato">MD{series.formato}</span>
        </div>

        {/* Centro: Ação atual */}
        <div className={`current-action ${draftAcabou || (DRAFT_ORDER[stepIndex]?.type === 'pick') ? 'fase-pick' : ''}`} id="currentActionBanner">
          <span className="ic" id="currentActionIcon">{draftAcabou ? '🏁' : (DRAFT_ORDER[stepIndex]?.type === 'pick' ? '⚔' : '🔒')}</span>
          Ação atual: <b id="actionLabel">{actionLabel()}</b>
        </div>

        {/* Direita: Ações de controle */}
        <div className="gamenav-right">
          <div className="icon-btn" title="Reiniciar draft deste jogo" onClick={() => { if(window.confirm('Reiniciar o draft deste jogo?')) draft.reiniciarJogoAtual(); }}>↺</div>
          <div className="icon-btn" title="Voltar à configuração da série" onClick={() => { if(window.confirm('Voltar para a configuração da série?')) series.setShowConfigModal(true); }}>🏠</div>
        </div>
      </div>

      {/* ---- BARRA DE INFO (Jogo atual, Próximo Jogo, Sugestões) ---- */}
      <div className="center-info-bar">
        <div className="bb-center">
          <span className="series-label">Jogo: <span id="gameCur">{series.jogoAtual}</span>/<span id="gameTot">{series.formato}</span></span>
          <div className="series-dots" id="seriesDots">
            {Array.from({length: series.formato}).map((_, i) => (
              <span key={i} className={i < series.jogoAtual - 1 ? 'done' : (i === series.jogoAtual - 1 ? 'current' : '')}></span>
            ))}
          </div>
        </div>
        
        <div className="bb-actions">
          <div 
            className={`bb-btn ${draftAcabou && (series.jogoAtual < series.formato) ? 'pulse-accent' : 'disabled-btn'}`} 
            id="nextGameBtn"
            onClick={draftAcabou && (series.jogoAtual < series.formato) ? handleNextGameAction : undefined}
          >
            {(series.jogoAtual >= series.formato) ? 'Série Finalizada' : 'Próximo Jogo ▶'}
          </div>
        </div>

        <div className="bb-right">
          <span className="switch-label">Destacar sugestões no grid</span>
          <div className={`switch ${suggestionsOn ? 'on' : ''}`} id="togglePickSuggest" onClick={() => setSuggestionsOn(!suggestionsOn)}></div>
        </div>
      </div>

      {/* ---- ÁREA PRINCIPAL (Times + Grid) ---- */}
      <div className="main">
        <TeamPanel 
          side="blue" 
          team={series.teamOnSide.blue} 
          picks={picksBySide.blue || []} 
          bans={bansBySide.blue || []} 
          isTurn={activeSide === 'blue'} 
        />

        <div className="center">
          <div className="tools-row">
            <div className="role-tabs" id="roleTabs">
              {['top', 'jng', 'mid', 'adc', 'sup'].map(r => (
                <div key={r} className={`role-tab ${activeRole === r ? 'active' : ''}`} onClick={() => setActiveRole(r)}>
                  {r.charAt(0).toUpperCase() + r.slice(1)}
                </div>
              ))}
            </div>
            <div className="search-wrap">
              <span className="ic">⌕</span>
              <input type="text" id="searchInput" placeholder="Buscar campeão..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
            </div>
            <button 
              type="button" 
              className={`confirm-pick-btn ${draft.pendingChampion && !draftAcabou ? 'ready' : ''}`}
              disabled={!draft.pendingChampion || draft.loading || draftAcabou} 
              onClick={draft.confirmarSelecao}
            >
              Confirmar
            </button>
            <button 
              type="button" 
              className="ia-joga-btn" 
              disabled={draftAcabou || draft.loading} 
              onClick={draft.iaJoga}
            >
              🤖 IA joga
            </button>
            <div className={`bb-btn ${draft.loading || stepIndex === 0 ? 'disabled-btn' : ''}`} onClick={draft.desfazer}>↺ Desfazer</div>
            <div className={`bb-btn ${draft.loading ? 'disabled-btn' : ''}`} onClick={draft.refazer}>↻ Refazer</div>
          </div>
          
          <div className="champ-grid-shell" id="champGridShell">
            <ChampionGrid 
              champions={draft.champions} 
              searchQuery={searchQuery} 
              bannedList={allBanned} 
              pendingChampion={draft.pendingChampion} 
              setPendingChampion={draft.setPendingChampion}
              suggestions={draft.sugestaoIA}
              suggestionsOn={suggestionsOn}
              isTurnForPlayer={isPlayerTurn}
            />
            <div className={`grid-loading-overlay ${draft.loading ? 'show' : ''}`} id="gridLoadingOverlay">
              <div className="spinner"></div>
              <div className="txt">{draft.loadingText || 'Carregando...'}</div>
            </div>
          </div>
        </div>

        <TeamPanel 
          side="red" 
          team={series.teamOnSide.red} 
          picks={picksBySide.red || []} 
          bans={bansBySide.red || []} 
          isTurn={activeSide === 'red'} 
        />
      </div>

      {/* ---- BARRA INFERIOR ---- */}
      <BottomBar 
        onOpenHistory={() => setHistoryPanelOpen(!historyPanelOpen)}
      />

      <HistoryDrawer 
        open={historyPanelOpen} 
        onClose={() => setHistoryPanelOpen(!historyPanelOpen)} 
        history={series.history} 
      />
    </div>
  );
}
