import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private apiUrl = 'http://localhost:5000';  // URL do FastAPI backend

  constructor(private http: HttpClient) {}

  sendQuestion(question: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/ask`, { question });
  }
}

