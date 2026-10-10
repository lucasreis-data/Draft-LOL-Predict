package com.lol.draft_lol.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.servlet.http.HttpServletRequest;

/**
 * Descobre o IP real de quem chamou.
 *
 * Em producao o caminho e: navegador -> CloudFront -> ALB -> Java. Cada salto acrescenta
 * um IP no fim do X-Forwarded-For:  [o que o cliente mandou...], IP-do-navegador, IP-do-CloudFront.
 * Quem confia na PRIMEIRA entrada deixa o cliente forjar o proprio IP. Por isso contamos a
 * partir da DIREITA, pulando so os proxies em que confiamos (draft.proxies-confiaveis = 2).
 * Sem o cabecalho (rodando local), usa o IP da conexao.
 */
@Component
public class IpCliente {

  private final int proxiesConfiaveis;

  public IpCliente(@Value("${draft.proxies-confiaveis:2}") int proxiesConfiaveis) {
    this.proxiesConfiaveis = proxiesConfiaveis;
  }

  public String resolver(HttpServletRequest request) {
    String cabecalho = request.getHeader("X-Forwarded-For");
    if (proxiesConfiaveis > 0 && cabecalho != null && !cabecalho.isBlank()) {
      String[] partes = cabecalho.split(",");
      int indice = partes.length - proxiesConfiaveis;
      if (indice >= 0) {
        String ip = partes[indice].trim();
        if (!ip.isEmpty()) {
          return ip;
        }
      }
    }
    return request.getRemoteAddr();
  }
}
