import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ChatService } from '../../services/chat.service';  // Importa o serviço
import { Router } from '@angular/router';




@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements AfterViewChecked {

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  messages: { role: 'user' | 'assistant'; content: string }[] = [];
  userInput: string = '';

  constructor(private chatService: ChatService, private router: Router) {}


  ngAfterViewChecked() {
    this.scrollToBottom();
  }
 

  sendMessage() {
    if (!this.userInput.trim()) return;
  
    this.messages.push({ role: 'user', content: this.userInput });
  
    // Criar a mensagem de loading com texto inicial
    const loadingMessage: { role: 'user' | 'assistant'; content: string } = {
      role: 'assistant',
      content: '.'
    };
    this.messages.push(loadingMessage);
  
    // Atualizar dinamicamente os pontos (animação de carregamento)
    const interval = setInterval(() => {
      if (loadingMessage.content.length < 3) {
        loadingMessage.content += '.';
      } else {
        loadingMessage.content = '.';
      }
    }, 500); // muda a cada meio segundo
  
    this.chatService.sendQuestion(this.userInput).subscribe({
      next: (response) => {
        clearInterval(interval); // parar animação
        const index = this.messages.indexOf(loadingMessage);
        if (index !== -1) {
          this.messages[index] = { role: 'assistant', content: response.response };
        }
      },
      error: (err) => {
        clearInterval(interval); // parar animação
        const index = this.messages.indexOf(loadingMessage);
        if (index !== -1) {
          this.messages[index] = { role: 'assistant', content: 'Erro ao comunicar com o servidor.' };
        }
      }
    });
  
    this.userInput = '';
  }

  private scrollToBottom() {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  adicionarMensagem(novaMensagem: any) {
    this.messages.push(novaMensagem);
    // A rolagem será tratada automaticamente pelo ngAfterViewChecked
  }

  goHome() {
    this.router.navigate(['/home']);
  }

  formatMessage(content: string): string {
    const regex = /http[s]?:\/\/[^\s]+/g;
    return content.replace(regex, (url) => {
      const updatedUrl = url.startsWith("https") ? url.replace("https", "http") : url;
      return `<a href="${updatedUrl}" target="_blank" rel="noopener noreferrer">Clique aqui para ver o documento</a>`;
    });
  }
  
  
  
}
