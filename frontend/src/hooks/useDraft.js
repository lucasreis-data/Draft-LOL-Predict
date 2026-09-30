import { useState, useEffect } from 'react';
import { draftService } from '../service/DraftService';

export function useDraft(series) {
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  
  const [sugestaoIA, setSugestaoIA] = useState({ tipo: null, campeoes: [] });
  const [dadosDraft, setDadosDraft] = useState(null);
  const [jogadorAtual, setJogadorAtual] = useState('PLAYER');
  
  const [champions, setChampions] = useState([]);
  const [ligasDisponiveis, setLigasDisponiveis] = useState([]);
  
  const [pendingChampion, setPendingChampion] = useState(null);
  
  useEffect(() => {
    draftService.getLigasDisponiveis()
      .then(res => setLigasDisponiveis(res.ligas || []))
      .catch(console.error);
      
    draftService.getChampions()
      .then(res => setChampions(res.map(nome => ({ name: nome }))))
      .catch(console.error);
  }, []);

  const fetchSession = async () => {
    if (!draftService.getSessionId()) return;
    try {
      const sessao = await draftService.sessao();
      setDadosDraft(sessao);
      setJogadorAtual(sessao.jogadorAtual);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSuggestion = async () => {
    if (!draftService.getSessionId()) return;
    try {
      const data = await draftService.sugestao();
      let camps = [];
      if (data && Array.isArray(data.champion)) {
        camps = data.champion;
      } else if (data && data.champion) {
        camps = [data.champion];
      }
      // Depending on phase, we might need to know if it's pick or ban
      // Assuming backend tells us or we infer from game state
      setSugestaoIA({ tipo: 'pick', campeoes: camps }); // simplification
    } catch (e) {
      console.error(e);
      setSugestaoIA({ tipo: null, campeoes: [] });
    }
  };

  const iniciarJogo = async (isFirstPick) => {
    setLoading(true);
    setLoadingText('Carregando modelo da liga... (pode levar alguns segundos)');
    try {
      if (series.jogoAtual === 1) {
        await draftService.iniciarDraft({
          quantidadeJogos: series.formato,
          isFirstPick: isFirstPick,
          timeUsuario: series.time1?.name,
          timeIA: series.time2?.name,
          liga: series.liga
        });
      } else {
        await draftService.proxJogo({
          sessionId: draftService.getSessionId(),
          isFirstPick: isFirstPick
        });
      }
      await fetchSession();
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const confirmarSelecao = async () => {
    if (!pendingChampion) return;
    setLoading(true);
    try {
      const res = await draftService.pickBanChampion({
        sessionId: draftService.getSessionId(),
        champion: pendingChampion
      });
      setDadosDraft(res);
      setJogadorAtual(res.jogadorAtual);
      setPendingChampion(null);
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const iaJoga = async () => {
    setLoading(true);
    try {
      const res = await draftService.pickBanChampion({
        sessionId: draftService.getSessionId()
      });
      setDadosDraft(res);
      setJogadorAtual(res.jogadorAtual);
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const desfazer = async () => {
    setLoading(true);
    try {
      const res = await draftService.desfazer({ sessionId: draftService.getSessionId() });
      setDadosDraft(res);
      setJogadorAtual(res.jogadorAtual);
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const refazer = async () => {
    setLoading(true);
    try {
      const res = await draftService.refazer({ sessionId: draftService.getSessionId() });
      setDadosDraft(res);
      setJogadorAtual(res.jogadorAtual);
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const reiniciarJogoAtual = async () => {
    setLoading(true);
    try {
      const res = await draftService.reiniciarJogo({ sessionId: draftService.getSessionId() });
      setDadosDraft(res);
      setJogadorAtual(res.jogadorAtual);
      await fetchSuggestion();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return {
    loading, loadingText,
    champions, ligasDisponiveis,
    dadosDraft, jogadorAtual, sugestaoIA,
    pendingChampion, setPendingChampion,
    iniciarJogo,
    confirmarSelecao, iaJoga, desfazer, refazer, reiniciarJogoAtual
  };
}
