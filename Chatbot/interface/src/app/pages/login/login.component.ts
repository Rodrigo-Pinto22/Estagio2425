import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  ipn: string = '';
  password: string = '';
  error: string = '';

  constructor(private router: Router) {}

  login() {
    if (this.ipn === 'admin' && this.password === '1234') {
      this.error = '';
      this.router.navigate(['/home']);
    } else {
      this.error = 'IPN ou Password incorretos.';
    }
  }
}

