const API_BASE_URL = 'http://localhost:5001';

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  research_result?: {
    recommendation: string;
    iterations: number;
    timestamp: string;
    error?: string;
  } | null;
  research_status: 'none' | 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string | null;
}

export interface ApiResponse {
  message?: string;
  status: string;
  data?: Task[];
}

export const fetchTasks = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

export const updateTask = async (
  id: number,
  payload: Partial<{ title: string; description: string; completed: boolean }>
): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

export const deleteTask = async (id: number): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};

export const deleteAllTasks = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/bulk-delete`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting all tasks:', error);
    throw error;
  }
};

export const saveNewTask = async (taskData: { title: string; description: string; }): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving new task:', error);
    throw error;
  }
};

export const seedMockTasks = async (source?: string, n?: number): Promise<ApiResponse> => {
  try {
    let url = `${API_BASE_URL}/api/tasks/seed`;
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    if (n) params.set('n', String(n));
    const query = params.toString();
    if (query) url += `?${query}`;

    const response = await fetch(url, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error seeding tasks:', error);
    throw error;
  }
};

export const clusterTasks = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/cluster`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error clustering tasks:', error);
    throw error;
  }
};

export const researchTask = async (taskId: number): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error researching task:', error);
    throw error;
  }
};
