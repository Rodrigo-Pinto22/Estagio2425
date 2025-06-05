import { Component, NgZone, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import * as Highcharts from 'highcharts';
import { HighchartsChartModule } from 'highcharts-angular';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-dashboard',
  imports: [FormsModule, HighchartsChartModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  constructor(private http: HttpClient, private router: Router, private zone: NgZone) {}
  goHome() {
    this.router.navigate(['/home']);
  }

  calcularMedia(dados: any[]): number {
    const total = dados.reduce((acc, curr) => acc + curr.horas, 0);
    return dados.length ? parseFloat((total / dados.length).toFixed(2)) : 0;
  }
  
  Highcharts: typeof Highcharts = Highcharts;
  chartOptions: Highcharts.Options = {};

  filtroMaquinas: string[] = [];
  filtroPeriodo: string = 'todos';
  todasMaquinas: string[] = [];
  dadosOriginais: any[] = [];
  dadosFiltrados: any[] = [];
  tempoMedio: number = 0;
  totalHoras: number = 0;
  totalIntervencao: number = 0;
  totalIntervencaoPorMaquina: { [key: string]: number } = {};

  ngOnInit(): void {
    this.http.get<any[]>('http://localhost:8000/api/tempo-intervencao')
      .subscribe(dados => {
        this.dadosOriginais = dados;
        this.todasMaquinas = [...new Set(dados.map(d => `${d.nome} ${d.modelo}`))];
        this.filtroMaquinas = [...this.todasMaquinas]; // seleção inicial: todas
        this.atualizarGrafico();
      });

      (window as any).angularComponentRef = {
        zone: this.zone,
        component: this
      };

      (window as any).angularComponentRef = {
        zone: this.zone,
        component: this,
        intervençõesPorMaquina: this.totalIntervencaoPorMaquina,
        dadosOriginais: this.dadosOriginais
      };

      this.totalHoras = this.dadosOriginais.reduce((acc, d) => acc + d.horas, 0);
      this.totalIntervencao = this.dadosOriginais.length;
      this.dadosOriginais.forEach(d => {
        const chave = `${d.nome} ${d.modelo}`;
        if (!this.totalIntervencaoPorMaquina[chave]) {
          this.totalIntervencaoPorMaquina[chave] = 0;
        }
        this.totalIntervencaoPorMaquina[chave]++;
      });

      
  }
  
  atualizarGrafico(): void {
    const ultimaData = new Date(Math.max(...this.dadosOriginais.map(d => new Date(d.data).getTime())));
    const diasFiltro = this.filtroPeriodo === 'todos' ? Infinity : parseInt(this.filtroPeriodo);
    
  
    const dadosFiltrados = this.dadosOriginais.filter(d => {
      const dataInterv = new Date(d.data);
      const diasDesde = (ultimaData.getTime() - dataInterv.getTime()) / (1000 * 60 * 60 * 24);
      const dentroDoTempo = diasFiltro === Infinity || diasDesde <= diasFiltro;
      const maquinaSelecionada = this.filtroMaquinas.includes(`${d.nome} ${d.modelo}`);
      console.log('Filtro:', diasFiltro, 'Data:', d.data, 'Dentro do tempo:', dentroDoTempo);
      return dentroDoTempo && maquinaSelecionada;
    });

    this.dadosFiltrados = dadosFiltrados;
    this.tempoMedio = this.calcularMedia(
      this.dadosFiltrados.length ? this.dadosFiltrados : this.dadosOriginais
    );
  
    const categories = [...new Set(dadosFiltrados.map(d => d.data))].sort();
    const maquinas = this.filtroMaquinas;
    const janelaMedia = 3; // podes ajustar para 5, 7, etc
  
    const series: Highcharts.SeriesOptionsType[] = maquinas.flatMap(maquina => {
      const dadosPorData = categories.map(data => {
        const item = dadosFiltrados.find(d => `${d.nome} ${d.modelo}` === maquina && d.data === data);
        return item ? item.horas : 0;
      });
    

    
      // série original
      const serieOriginal: Highcharts.SeriesLineOptions = {
        name: maquina,
        type: 'line',
        data: dadosPorData,
        visible: false,
      };
    
      // série média móvel
      const mediaMovel: number[] = [];
      for (let i = 0; i < dadosPorData.length; i++) {
        const inicio = Math.max(0, i - janelaMedia + 1);
        const slice = dadosPorData.slice(inicio, i + 1);
        const media = slice.reduce((a, b) => a + b, 0) / slice.length;
        mediaMovel.push(+media.toFixed(2));
      }
    
      const serieMedia: Highcharts.SeriesLineOptions = {
        name: `${maquina} (média móvel)`,
        type: 'line',
        dashStyle: 'ShortDash',
        color: 'gray',
        data: mediaMovel,
        marker: { enabled: false },
        visible: false,
      };
    
      return [serieOriginal, serieMedia];
    });
    
  
    this.chartOptions = {
      chart: { type: 'line'},
      title: { text: '' },
      xAxis: { categories, title: { text: 'Data' } },
      yAxis: { min: 0, title: { text: 'Horas' } },
      credits: { enabled: false },
      customDataOriginal: this.dadosOriginais,
      plotOptions: {
        series: {
          events: {
            legendItemClick: function (this: Highcharts.Series): boolean {
              const chart = this.chart;
              const scope = (window as any).angularComponentRef;
            
              const seriesVisiveis = chart.series.filter(
                s => s.visible && !s.name.includes('média móvel')
              );
            
              const dadosOriginais = scope.component.dadosOriginais;
              const intervençõesPorMaquina = scope.component.totalIntervencaoPorMaquina;
            
              let dadosSelecionados: any[] = [];
              let nomeSerie = '';
            
              if (seriesVisiveis.length === 1) {
                nomeSerie = seriesVisiveis[0].name.trim();
            
                dadosSelecionados = dadosOriginais.filter(
                  (d: any) => `${d.nome} ${d.modelo}` === nomeSerie
                );
              } else {
                dadosSelecionados = dadosOriginais;
              }
            
              const media = dadosSelecionados.reduce((acc: number, d: any) => acc + d.horas, 0) / dadosSelecionados.length;
              const mediaFinal = Number(media.toFixed(2));
              const totalHoras = dadosSelecionados.reduce((acc: number, d: any) => acc + d.horas, 0);
              const totalIntervencoes = seriesVisiveis.length === 1
                ? intervençõesPorMaquina[nomeSerie] || 0
                : dadosOriginais.length;
            
              if (scope) {
                scope.zone.run(() => {
                  scope.component.tempoMedio = mediaFinal;
                  scope.component.totalHoras = totalHoras;
                  scope.component.totalIntervencoes = totalIntervencoes;
                });
              }
            
              return true;
            }            
          }
        }
      },
      series
    }as any;
  };
}



