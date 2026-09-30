import { useState } from 'react';

export function useSeries() {
  const [showConfigModal, setShowConfigModal] = useState(true);
  const [showStartModal, setShowStartModal] = useState(false);
  const [showEndModal, setShowEndModal] = useState(false);

  const [liga, setLiga] = useState('CBLOL');
  const [timesDisponiveis, setTimesDisponiveis] = useState([]);
  
  const [time1, setTime1] = useState(null);
  const [time2, setTime2] = useState(null);
  const [formato, setFormato] = useState(5);
  
  const [jogoAtual, setJogoAtual] = useState(1);
  const [ladoFirstPick, setLadoFirstPick] = useState('blue');
  const [teamOnSide, setTeamOnSide] = useState({ blue: null, red: null });
  const [history, setHistory] = useState([]);

  const finishConfig = (t1, t2, f, lig) => {
    setTime1(t1);
    setTime2(t2);
    setFormato(f);
    setLiga(lig);
    setJogoAtual(1);
    setHistory([]);
    setShowConfigModal(false);
    setShowStartModal(true);
  };

  const startNextGame = (side, isFpTime1) => {
    // side: 'blue' | 'red' for time1
    const otherSide = side === 'blue' ? 'red' : 'blue';
    setTeamOnSide({
      [side]: time1,
      [otherSide]: time2
    });
    setLadoFirstPick(isFpTime1 ? side : otherSide);
    setShowStartModal(false);
  };

  const finishGame = (gameData) => {
    setHistory(prev => [...prev, { ...gameData, jogo: jogoAtual }]);
    if (jogoAtual >= formato) {
      setShowEndModal(true);
    }
  };

  const nextGameModal = () => {
    if (jogoAtual < formato) {
      setJogoAtual(prev => prev + 1);
      setShowStartModal(true);
    }
  };

  const resetSeries = () => {
    setShowEndModal(false);
    setShowConfigModal(true);
  };

  return {
    showConfigModal, setShowConfigModal,
    showStartModal, setShowStartModal,
    showEndModal, setShowEndModal,
    liga, setLiga,
    timesDisponiveis, setTimesDisponiveis,
    time1, time2,
    formato,
    jogoAtual,
    ladoFirstPick,
    teamOnSide,
    history,
    finishConfig,
    startNextGame,
    finishGame,
    nextGameModal,
    resetSeries
  };
}
