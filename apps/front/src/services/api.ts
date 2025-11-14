const API_BASE_URL = 'http://localhost:5001';

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
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
}
