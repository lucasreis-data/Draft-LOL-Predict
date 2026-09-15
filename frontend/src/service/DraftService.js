const BASE_URL = 'http://localhost:8080/draft'

let sessionIdGlobal = null;
export const draftService = {
    iniciarDraft: async (dados) => {
        const resposta = await fetch (`${BASE_URL}/Start`,{
             method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify(dados)
        })
        const dadosResposta = await resposta.json()
        sessionIdGlobal = dadosResposta.sessionId
        return dadosResposta;
    },

    getSessionId: () => sessionIdGlobal,

    pickBanChampion: async (dados) => {
        const resposta = await fetch (`${BASE_URL}/Picks-Bans`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        return await resposta.json()            
        
    },

    getChampions: async(dados) => {
        const response = await fetch (`${BASE_URL}/champions`)
        return await response.json()
    },

    getTimes: async(liga) => {
        const response = await fetch (`${BASE_URL}/times?liga=${liga}`)
        return await response.json()
    },

    getLigasDisponiveis: async() => {
        const response = await fetch(`${BASE_URL}/ligas/disponiveis`)
        return await response.json()
    },

    proxJogo: async(dados) => {
        const response = await fetch (`${BASE_URL}/Prox-jogo`,{
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        return await response.json()
    },

    sugestao: async() => {
        const id = sessionIdGlobal
        const response = await fetch (`${BASE_URL}/Sugestao?sessionId=${id}`)
        return await response.json()
    },

    sessao: async() => {
        const id = sessionIdGlobal
        const response = await fetch (`${BASE_URL}/sessao?sessionId=${id}`)
        return await response.json()
    },
    jogadorAtual: async() => {
        const id = sessionIdGlobal
        const response = await fetch (`${BASE_URL}/sessao?sessionId=${id}`)
        const dadosResposta = await response.json()
        return dadosResposta.jogadorAtual
        
    }
}