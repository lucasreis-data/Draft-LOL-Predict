import {use, useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import { draftService } from './service/DraftService'
import BlueTeam from './components/BlueTeam/BlueTeam'
import RedTeam from './components/RedTeam/RedTeam'
import ChampionsSelection from './components/ChampionsSelection/ChampionsSelection'

const times = [
  { name: 'LOUD' },
  { name: 'FURIA' }
];



function App() {

  const [sugestaoIA, setSugestaoIA] = useState([]);
  const [dadosDraftJava, setDadosDraftJava] = useState(null);
  const [jogadorAtual, setJogadorAtual] = useState('PLAYER');
  const [buscarChamp, setBuscarChamp] = useState('');
  const [ligaEscolhido, setLigaEscolhida] = useState('CBLOL')
  const [ligaDisponiveis, setLigasDisponiveis] = useState([])

  useEffect(() => {
  if (draftService.getSessionId()) {
    draftService.jogadorAtual().then(jogador => {
      if (jogador) setJogadorAtual(jogador)
    })
  }
}, [])

  useEffect(() => {
  if (draftService.getSessionId()) {
    draftService.sessao().then(sessao => {
      if (sessao) setDadosDraftJava(sessao)
    })
  }
}, [])

  useEffect(() => {
    if (dadosDraftJava) {
      obterSugestao();
    }
  }, [dadosDraftJava]);

  useEffect(() => {
    const carregarLigas = async() => {
      try {
        const lista = await draftService.getLigasDisponiveis()
      setLigasDisponiveis(lista.ligas)
      } catch(e){
        console.error("Erro ao buscar ligas: ", e)
        setLigasDisponiveis([])
      }
    }
    carregarLigas()
  }, [])

const obterSugestao = async () => {
  try {
    const data = await draftService.sugestao();
    if (data && Array.isArray(data.champion)) {
      setSugestaoIA(data.champion);
    } else if (data && data.champion) {
      setSugestaoIA([data.champion]);
    }
  } catch (error) {
    console.error("Erro ao buscar sugestão da IA", error);
  }
};


  const [champions, setChampions] = useState([])

  useEffect(() => {
    const carregarCampeoes = async () => {
      try {
        const listNomes = await draftService.getChampions()
        setChampions(listNomes.map(nome=> ({name: nome})))
      } catch (e) {
        console.error("erro ao buscar campeoes: ", e)
      }
    }
    carregarCampeoes()
  }, [])

  const champsFiltrados = champions.filter((champ) => champ.name.toLowerCase().includes(buscarChamp.toLowerCase()));
  const [times, setTimes] = useState([])

  useEffect(() => {
    const carregarTimes = async () => {
      try {
        const listNomes = await draftService.getTimes(ligaEscolhido)
        setTimes(listNomes.map(nome=> ({name: nome})))
      } catch (e) {
        console.error("erro ao buscar times: ", e)
      }
    }
    carregarTimes()
  }, [ligaEscolhido])
  const[selecaoTemporaria, setSelecaoTemporaria] = useState(null)
  

  const tratarCliqueNoChamp = (champion) => {
    setSelecaoTemporaria(champion)
  }
  const confirmarSelecao = async () => {
    if(!selecaoTemporaria) return
    setChampsBloqueados([...champsBloqueados, selecaoTemporaria.name])
    setSelecaoTemporaria(null)
    setSugestaoIA([])
  }

  const[champsBloqueados, setChampsBloqueados] = useState([])
  const pickBanChamp = async () => {
    const pickBan = {
      sessionId: draftService.getSessionId(),
      champion: selecaoTemporaria.name
    }
    try{
      const resultado = await draftService.pickBanChampion(pickBan)
      console.log("enviando...", resultado)
      setDadosDraftJava(resultado)
      setSelecaoTemporaria(null)
      const novosProibidos = [
            ...(resultado.bansIA || []),
            ...(resultado.bansPlayer || []),
            ...(resultado.fearless || []),
        ];
        
        setChampsBloqueados(novosProibidos);
        setJogadorAtual(resultado.jogadorAtual)
    } catch(error){
      console.error("falha no backend", error)
    }

  }
  const pickBanChampIA = async () => {
    const pickBan = {
      sessionId: draftService.getSessionId()
    }
    try{
      const resultado = await draftService.pickBanChampion(pickBan)
      console.log("enviando...", resultado)
      setDadosDraftJava(resultado)
       const novosProibidos = [
            ...(resultado.bansIA || []),
            ...(resultado.bansPlayer || []),
            ...(resultado.fearless || []),
        ];
        
        setChampsBloqueados(novosProibidos);
        setJogadorAtual(resultado.jogadorAtual)
    } catch(error){
      console.error("falha no backend", error)
    }

  }

  const nextJogo = async () =>{
    const dados = {
      sessionId: draftService.getSessionId(),
      isFirstPick: ladoFirstPick === 'BLUE'
    }
    try{
      const resultado = await draftService.proxJogo(dados)
      const novosProibidos = [dadosDraftJava.fearless];
      setChampsBloqueados(novosProibidos);
      setJogadorAtual(resultado.jogadorAtual)
    }catch(error){
      console.error("falha no backend", error)
    }

  }

  const iniciarDraft = async () =>{
     const dadosDraft = {
      timeUsuario: timeConfirmadoBlue.name,
      timeIA: timeConfirmadoRed.name,
      quantidadeJogos: formatoMD,
      isFirstPick: ladoFirstPick === 'BLUE',
      liga: ligaEscolhido
    }
    try{
      const resultado = await draftService.iniciarDraft(dadosDraft)
      console.log("enviando para o java", resultado)
      obterSugestao()
      setJogadorAtual(resultado.jogadorAtual)
    } catch(error){
      console.error("falha ao iniciar draft no backend", error)
    }

  }
  
  let textoBotao = "selecione um campeao"
  let botaoDesabilitado = true
  
  if(selecaoTemporaria != null){
    textoBotao = "confirmar " + selecaoTemporaria.name
    botaoDesabilitado = false;
  }

  const [formatoMD, setFormatoMD] = useState(5)

  const[ladoFirstPick, setLadoFirstPick] = useState('BLUE')

  const [buscaTimeBlue, setBuscaTimeBlue] = useState('');
  const [timeEscolhidoBlue, setTimeEscolhidoBlue] = useState(null);



  const [timeTempBlue, setTimeTempBlue] = useState(null);
  const [timeConfirmadoBlue, setTimeConfirmadoBlue] = useState(null);


  const [timeTempRed, setTimeTempRed] = useState(null);
  const [timeConfirmadoRed, setTimeConfirmadoRed] = useState(null);
 
  

  const confirmarTimeBlue = () => {
    if (timeTempBlue != null) {
      setTimeConfirmadoBlue(timeTempBlue);
      setTimeTempBlue(null); 
    }
  };

  const confirmarTimeRed = () => {
    if (timeTempRed != null) {
      setTimeConfirmadoRed(timeTempRed);
      setTimeTempRed(null); 
    }
  };
  let timeDaVez = "Aguardando escolha: ";
  if (jogadorAtual === 'PLAYER' && timeConfirmadoBlue) {
    timeDaVez += timeConfirmadoBlue.name;
  } else if (jogadorAtual === 'IA' && timeConfirmadoRed) {
    timeDaVez += timeConfirmadoRed.name;
  }

  return (
    <div className='main-container app-main-wrapper'>
      <BlueTeam 
        timeConfirmadoBlue={timeConfirmadoBlue}
        timeConfirmadoRed={timeConfirmadoRed}
        times={times}
        timeTempBlue={timeTempBlue}
        setTimeTempBlue={setTimeTempBlue}
        confirmarTimeBlue={confirmarTimeBlue}
        ladoFirstPick={ladoFirstPick}
        setLadoFirstPick={setLadoFirstPick}
        dadosDraftJava={dadosDraftJava}
      />

      <ChampionsSelection 
        ligaEscolhido={ligaEscolhido}
        setLigaEscolhida={setLigaEscolhida}
        ligaDisponiveis={ligaDisponiveis}
        formatoMD={formatoMD}
        setFormatoMD={setFormatoMD}
        timeConfirmadoBlue={timeConfirmadoBlue}
        timeConfirmadoRed={timeConfirmadoRed}
        iniciarDraft={iniciarDraft}
        timeDaVez={timeDaVez}
        buscarChamp={buscarChamp}
        setBuscarChamp={setBuscarChamp}
        confirmarSelecao={confirmarSelecao}
        pickBanChamp={pickBanChamp}
        botaoDesabilitado={botaoDesabilitado}
        textoBotao={textoBotao}
        pickBanChampIA={pickBanChampIA}
        nextJogo={nextJogo}
        champsFiltrados={champsFiltrados}
        champsBloqueados={champsBloqueados}
        selecaoTemporaria={selecaoTemporaria}
        sugestaoIA={sugestaoIA}
        tratarCliqueNoChamp={tratarCliqueNoChamp}
      />

      <RedTeam 
        timeConfirmadoRed={timeConfirmadoRed}
        timeConfirmadoBlue={timeConfirmadoBlue}
        times={times}
        timeTempRed={timeTempRed}
        setTimeTempRed={setTimeTempRed}
        confirmarTimeRed={confirmarTimeRed}
        ladoFirstPick={ladoFirstPick}
        setLadoFirstPick={setLadoFirstPick}
        dadosDraftJava={dadosDraftJava}
      />
    </div>
  )
}

export default App
