// Projeto 1: Recuperação dos Dados Originais (JavaScript)

// 1. Importação de Módulos Necessários
const fs = require('fs'); // Para leitura e escrita de arquivos
const pdf = require('pdfkit'); // Para gerar relatórios em PDF
const path = require('path'); // Para lidar com caminhos de arquivos

// 2. Função para ler os arquivos JSON
function lerArquivoJSON(caminhoArquivo) {
    try {
        const dados = fs.readFileSync(caminhoArquivo, 'utf8');
        return JSON.parse(dados);
    } catch (erro) {
        console.error(`Erro ao ler o arquivo ${caminhoArquivo}:`, erro);
        return null;
    }
}

// 3. Função para corrigir os dados do banco
function corrigirDados(bancoDeDados, tipo) {
    return bancoDeDados.map(registro => {
        if (tipo === 'veiculos') {
            // Corrigir os nomes dos veículos
            registro.nome = registro.nome.replace(/æ/g, 'a').replace(/ø/g, 'o');
            // Corrigir o tipo de vendas
            if (typeof registro.vendas === 'string') {
                registro.vendas = Number(registro.vendas);
            }
        } else if (tipo === 'marcas') {
            // Corrigir os nomes das marcas
            registro.marca = registro.marca.replace(/æ/g, 'a').replace(/ø/g, 'o');
        }
        return registro;
    });
}

// 4. Função para salvar os dados corrigidos em um novo arquivo JSON
function salvarArquivoJSON(caminhoArquivo, dados) {
    try {
        fs.writeFileSync(caminhoArquivo, JSON.stringify(dados, null, 2), 'utf8');
        console.log(`Arquivo corrigido salvo em: ${caminhoArquivo}`);
    } catch (erro) {
        console.error(`Erro ao salvar o arquivo ${caminhoArquivo}:`, erro);
    }
}

// 5. Função para salvar os dados corrigidos em CSV
function salvarArquivoCSV(caminhoArquivo, dados) {
    try {
        const headers = Object.keys(dados[0]); // Pega os nomes das colunas
        const linhas = dados.map(obj => headers.map(h => obj[h]).join(',')); // Cria as linhas

        // Junta os headers e as linhas
        const csv = [headers.join(','), ...linhas].join('\n');

        // Salva o arquivo CSV
        fs.writeFileSync(caminhoArquivo, csv, 'utf8');
        console.log(`Arquivo CSV gerado em: ${caminhoArquivo}`);
    } catch (erro) {
        console.error(`Erro ao salvar o arquivo CSV ${caminhoArquivo}:`, erro);
    }
}

// 6. Função para gerar relatório em PDF
function gerarRelatorioPDF(dados, caminhoRelatorio, titulo) {
    try {
        const doc = new pdf();
        const writeStream = fs.createWriteStream(caminhoRelatorio);
        doc.pipe(writeStream);

        // Título do relatório
        doc.fontSize(20).text(titulo, { align: 'center' });
        doc.moveDown();

        // Adicionar informações dos dados corrigidos
        dados.forEach((registro, index) => {
            doc.fontSize(12).text(`Registro ${index + 1}:`);
            Object.entries(registro).forEach(([chave, valor]) => {
                doc.text(`${chave}: ${valor}`);
            });
            doc.moveDown();
        });

        // Finalizar o documento
        doc.end();
        console.log(`Relatório gerado em: ${caminhoRelatorio}`);
    } catch (erro) {
        console.error(`Erro ao gerar o relatório PDF:`, erro);
    }
}

// 7. Fluxo Principal
function processarArquivos() {
    const arquivos = [
        { caminho: './broken_database_1.json', tipo: 'veiculos', titulo: 'Relatório de Veículos' },
        { caminho: './broken_database_2.json', tipo: 'marcas', titulo: 'Relatório de Marcas' }
    ];

    arquivos.forEach(({ caminho, tipo, titulo }) => {
        const caminhoEntrada = path.resolve(caminho);
        const caminhoSaidaJSON = path.resolve(`./corrigido_${path.basename(caminho)}`);
        const caminhoSaidaCSV = path.resolve(`./corrigido_${path.basename(caminho, '.json')}.csv`);
        const caminhoRelatorio = path.resolve(`./relatorio_${path.basename(caminho, '.json')}.pdf`);

        // Ler o arquivo original
        const bancoDeDados = lerArquivoJSON(caminhoEntrada);

        if (bancoDeDados) {
            // Corrigir os dados
            const bancoCorrigido = corrigirDados(bancoDeDados, tipo);

            // Salvar o arquivo corrigido em JSON
            salvarArquivoJSON(caminhoSaidaJSON, bancoCorrigido);

            // Salvar o arquivo corrigido em CSV
            salvarArquivoCSV(caminhoSaidaCSV, bancoCorrigido);

            // Gerar relatório em PDF
            gerarRelatorioPDF(bancoCorrigido, caminhoRelatorio, titulo);
        }
    });
}

// Executar o processamento
processarArquivos();
