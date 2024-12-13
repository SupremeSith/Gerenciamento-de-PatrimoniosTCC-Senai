// Função para aplicar o efeito de fade-in ao entrar na página
document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    // Configura o estilo inicial para ocultar a página
    body.style.opacity = 0;

    // Quando o conteúdo estiver pronto, aplica o efeito de fade-in
    setTimeout(() => {
        body.style.transition = 'opacity 0.5s ease-in-out';
        body.style.opacity = 1;
    }, 100); // Pequeno atraso para garantir que o estilo inicial seja aplicado
});
// Função para aplicar o efeito de entrada suave
document.addEventListener('DOMContentLoaded', () => {
    const items = document.querySelectorAll('.fade-in-item');

    // Adiciona a classe que inicia a animação
    items.forEach(item => {
        setTimeout(() => {
            item.classList.add('visible');
        }, 100); // Pequeno atraso para o efeito de suavidade
    });
});
