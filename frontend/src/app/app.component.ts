import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'MLOps Control Center';
  models: any[] = [];
  deployments: any[] = [];
  selectedModel: any = null;
  selectedVersion: any = null;
  errorMessage = '';
  loading = false;

  modelForm = {
    name: '',
    framework: 'xgboost',
    algorithm: 'gradient_boosting',
    owner: 'ml-ops',
    description: ''
  };

  versionForm = {
    version: 'v1.0.0',
    artifact_uri: 's3://models/demo-model',
    training_data_ref: 'warehouse:training:2024-09',
    framework: 'xgboost',
    algorithm: 'gradient_boosting',
    metadata: '{"accuracy": 0.93}'
  };

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadModels();
    this.loadDeployments();
  }

  loadModels(): void {
    this.loading = true;
    this.http.get<{ items: any[] }>('http://localhost:8000/models')
      .subscribe({
        next: (response) => {
          this.models = response.items ?? [];
          if (this.models.length && !this.selectedModel) {
            this.selectModel(this.models[0]);
          }
          this.loading = false;
        },
        error: () => {
          this.errorMessage = 'Unable to load models from the backend.';
          this.loading = false;
        }
      });
  }

  loadDeployments(): void {
    this.http.get<{ items: any[] }>('http://localhost:8000/deployments')
      .subscribe({
        next: (response) => {
          this.deployments = response.items ?? [];
        },
        error: () => {
          this.errorMessage = 'Unable to load deployment history.';
        }
      });
  }

  selectModel(model: any): void {
    this.selectedModel = model;
    this.http.get<{ items: any[] }>(`http://localhost:8000/models/${model.id}/versions`)
      .subscribe((response) => {
        const versions = response.items ?? [];
        this.selectedVersion = versions[0] ?? null;
        this.selectedModel.versions = versions;
      });
  }

  createModel(): void {
    this.http.post('http://localhost:8000/models', this.modelForm)
      .subscribe({
        next: () => {
          this.modelForm = {
            name: '',
            framework: 'xgboost',
            algorithm: 'gradient_boosting',
            owner: 'ml-ops',
            description: ''
          };
          this.loadModels();
        },
        error: () => {
          this.errorMessage = 'A model with that name already exists.';
        }
      });
  }

  createVersion(): void {
    if (!this.selectedModel) {
      this.errorMessage = 'Select a model before registering a version.';
      return;
    }

    const payload = {
      ...this.versionForm,
      metadata: JSON.parse(this.versionForm.metadata || '{}')
    };

    this.http.post(`http://localhost:8000/models/${this.selectedModel.id}/versions`, payload)
      .subscribe({
        next: () => {
          this.versionForm = {
            version: 'v1.0.0',
            artifact_uri: 's3://models/demo-model',
            training_data_ref: 'warehouse:training:2024-09',
            framework: 'xgboost',
            algorithm: 'gradient_boosting',
            metadata: '{"accuracy": 0.93}'
          };
          this.selectModel(this.selectedModel);
        },
        error: () => {
          this.errorMessage = 'Version creation failed. Check the model and metadata values.';
        }
      });
  }

  approveVersion(version: any): void {
    this.http.post(
      `http://localhost:8000/models/${this.selectedModel.id}/versions/${version.id}/approve`,
      { approved: true }
    ).subscribe(() => this.selectModel(this.selectedModel));
  }

  deployVersion(version: any, environment: string): void {
    this.http.post('http://localhost:8000/deployments', {
      model_id: this.selectedModel.id,
      version_id: version.id,
      environment,
      requested_by: 'ops-console'
    }).subscribe({
      next: () => {
        this.loadDeployments();
        this.errorMessage = '';
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail ?? 'Deployment could not be created.';
      }
    });
  }

  retryDeployment(id: number): void {
    this.http.post(`http://localhost:8000/deployments/${id}/retry`, {})
      .subscribe(() => this.loadDeployments());
  }

  rollbackDeployment(id: number): void {
    this.http.post(`http://localhost:8000/deployments/${id}/rollback`, {})
      .subscribe(() => this.loadDeployments());
  }
}
