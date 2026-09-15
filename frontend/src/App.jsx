import {use, useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import { draftService } from './service/DraftService'

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
        const listNomes = await draftService.getTimes()
        setTimes(listNomes.map(nome=> ({name: nome})))
      } catch (e) {
        console.error("erro ao buscar campeoes: ", e)
      }
    }
    carregarTimes()
  }, [])
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

    <div className='main-container'>
      <aside className='blue-team'>
        <h2>{timeConfirmadoBlue ? timeConfirmadoBlue.name : "Blue Side"}</h2>
        <header className='search-header'>
          <input 
          type="text" 
          placeholder='Pesquisar time...' 
          />
          
          {(timeConfirmadoBlue === null || timeConfirmadoRed=== null || timeConfirmadoBlue.name === timeConfirmadoRed.name) && (
            <div className='selecao-time-container'>
            <div className='times-lista'>
              {times.map((time) => {
                let classeTime = "time-card"
                if(timeTempBlue != null && timeTempBlue.name === time.name){
                  classeTime = "time-card selected-blue"
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
            className='btn-confirmar-time'
            onClick ={confirmarTimeBlue}
            disabled={timeTempBlue === null}  
              >
                Confirmar time azul
              
            </button>

          </div>
          )

          }
        </header>
        <header className="filter-header">
          <label>
            <input type="checkbox" 
            checked = {ladoFirstPick === 'BLUE'}
            onChange={() => setLadoFirstPick('BLUE')}
            /> é first pick?
          </label>
        </header>
        <div className='bans'>
          <h3>Seus Bans</h3>
          {dadosDraftJava?.bansPlayer?.map((nomeChamp, index) =>(
            <div key={index} className='ban-item'> {nomeChamp}</div>
          ))}
        </div>
        <div className='picks'>
          <h3>Seus Picks</h3>
          {dadosDraftJava?.picksPlayer?.map((nomeChamp, index) =>(
            <div key={index} className='pick-item'> {nomeChamp}</div>
          ))}
        </div>
        
      </aside>

      <main className='champions-selection'>
        <header className="filter-header">
          <select value = {ligaEscolhido} onChange={(e) => setLigaEscolhida(e.target.value)}>
            {ligaDisponiveis.map((liga) =>(
              <option key = {liga} value = {liga}>
                {liga}
              </option>
            ))}
          </select>
          <label>
            <input type="checkbox" checked={formatoMD === 1}
            onChange={() => setFormatoMD(1)} /> MD1
          </label>
          <label>
            <input type="checkbox" checked={formatoMD === 3}
            onChange={() => setFormatoMD(3)} /> MD3
          </label>
          <label>
            <input type="checkbox" checked={formatoMD === 5}
            onChange={() => setFormatoMD(5)} /> MD5
          </label>
          {(timeConfirmadoBlue !== null && timeConfirmadoRed !== null && timeConfirmadoBlue.name !== timeConfirmadoRed.name) && (
            <button className='bn-iniciar-draft'
            onClick={iniciarDraft}>
              iniciarDraft
            </button>
          )}
    

          <h3>{timeDaVez}</h3>
        </header>
        <p>champs banidos pelo fearless</p>
        <h2>Picks e Bans</h2>
        <header className='search-header'>
          <input 
          value={buscarChamp}
          onChange={(e) => setBuscarChamp(e.target.value)}
          type="text" 
          placeholder='Pesquisar campeao...' 
          />
          <div className='confirm-area'>
            <button
            className='btn-confirmar'
            onClick={() => {
              confirmarSelecao();
              pickBanChamp();
            }}
            disabled={botaoDesabilitado}>
              {textoBotao}
            </button>
          </div>
          <div className='confirm-area'>
            <button className='btn-jogar-ia'
            onClick={pickBanChampIA}>
              IA joga
            </button>
          </div>
          <div className= 'prox-jogo'>
            <button className='btn-prox-jogo'
            onClick={nextJogo}>
              PROX JOGO
            </button>
          </div>
        </header>
        <header className="filter-header">
          <input type="checkbox" id="top" name="position" />Top
          <input type="checkbox" id="Jungle" name="position" />Jungle
          <input type="checkbox" id="Mid" name="position" />Mid
          <input type="checkbox" id="Adc" name="position" />Adc
          <input type="checkbox" id="Sup" name="position" />Sup
        </header>

        <p>lista de champs</p>
        <div className='champions-grid'>
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

            let classeFinal = "champion-card"
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

      <aside className='red-team'>
        <h2> {timeConfirmadoRed ? timeConfirmadoRed.name : "Red Side"} </h2>
        <header className='search-header'>
          <input 
          type="text" 
          placeholder='Pesquisar time...' 
          />
          {(timeConfirmadoBlue === null || timeConfirmadoRed=== null || timeConfirmadoBlue.name === timeConfirmadoRed.name) && (
            <div className='selecao-time-container'>
            <div className='times-lista'>
              {times.map((time) => {
                let classeTime = "time-card"
                if(timeTempRed != null && timeTempRed.name === time.name){
                  classeTime = "time-card selected-red"
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
            className='btn-confirmar-time'
            onClick ={confirmarTimeRed}
            disabled={timeTempRed === null}  
              >
                Confirmar time vermelho
              
            </button>
          </div>

          )}
          

        </header>
        <header className="filter-header">
          <label>
            <input type="checkbox" 
            checked = {ladoFirstPick === 'RED'}
            onChange={() => setLadoFirstPick('RED')}
            /> é first pick?
          </label>
        </header>
         <div className='bans'>
          <h3>Bans IA</h3>
          {dadosDraftJava?.bansIA?.map((nomeChamp, index) =>(
            <div key={index} className='ban-item'> {nomeChamp}</div>
          ))}
        </div>
       <div className='picks'>
          <h3>Picks IA</h3>
          {dadosDraftJava?.picksIA?.map((nomeChamp, index) =>(
            <div key={index} className='pick-item'> {nomeChamp}</div>
          ))}
        </div>
        
      </aside>
    </div>
    
  )
}

export default App
