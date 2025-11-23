import { useState, useEffect } from 'react'
import { fetchTasks, ApiResponse, saveNewTask, deleteTask, updateTask, seedMockTasks, clusterTasks } from './services/api'
import AddNewTaskButton from './components/AddNewTaskButton';
import AddNewTaskDialog from './components/AddNewTaskDialog';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<boolean>(false);
  const [taskTitle, setTaskTitle] = useState<string>('');
  const [taskDescription, setTaskDescription] = useState<string>('');

  const handleClose = () => {
    setOpen(false);
    // Clear the inputs when closing
    setTaskTitle('');
    setTaskDescription('');
    setEditingTaskId(null);
  }

  const handleOpen = () => {  
    setOpen(true);
  }
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetchTasks();
        setData(response);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data from backend');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSave = async () => {
    try {
      if (editingTaskId !== null) {
        await updateTask(editingTaskId, {
          title: taskTitle,
          description: taskDescription,
        });
        setEditingTaskId(null);
      } else {
        await saveNewTask({
          title: taskTitle,
          description: taskDescription,
        });
      }
      // Refresh the task list to show the newly created task
      const updatedData = await fetchTasks();
      setData(updatedData);
      setClusters(null);  // Clear clusters when tasks are modified
      handleClose();
    } catch (err) {
      console.error('Error saving task:', err);
    }
  };

  const handleSeedData = async () => {
    console.log('handleSeedData called')
    try {
      // Request LLM-generated mock tasks (source=llm) and create 70 tasks
      const res = await seedMockTasks('llm', 20);
      console.log('seedMockTasks response:', res);
      const updated = await fetchTasks();
      setData(updated);
      setClusters(null);
      // Removed alert popup after seeding
      await fetchTasks();
    } catch (err) {
      console.error('Seeding failed:', err);
      alert('Seeding failed: ' + (err as any).toString());
    }
  };

  const handleClusterTasks = async () => {
    try {
      setClusteringLoading(true);
      const result = await clusterTasks();
      setClusters(result.clusters);
    } catch (err) {
      console.error('Clustering failed:', err);
      alert(`Clustering failed: ${err}`);
    } finally {
      setClusteringLoading(false);
    }
  };

  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [clusters, setClusters] = useState<{ [key: string]: any[] } | null>(null);
  const [clusteringLoading, setClusteringLoading] = useState(false);
  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>My amazing TODO app</h1>

      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <AddNewTaskButton onClick={handleOpen} />
          <button onClick={handleSeedData} style={{ padding: '10px 20px', cursor: 'pointer' }}>
            Load 20 Mock Tasks
        </button>
        <button 
          onClick={handleClusterTasks} 
          disabled={clusteringLoading}
          style={{ padding: '10px 20px', cursor: 'pointer', opacity: clusteringLoading ? 0.5 : 1 }}
        >
          {clusteringLoading ? 'Clustering...' : 'Cluster Tasks with AI'}
        </button>
      </div>

      {/* Display clustered tasks */}
      {clusters && (
        <div style={{ marginBottom: '20px', backgroundColor: '#f5f5f5', padding: '15px', borderRadius: '4px' }}>
          <h2>Clustered Tasks (by AI)</h2>
          {Object.entries(clusters).map(([category, tasks]) => (
            <div key={category} style={{ marginBottom: '20px', borderLeft: '4px solid #007bff', paddingLeft: '15px' }}>
              <h3 style={{ margin: '10px 0 10px 0' }}>{category} ({tasks.length})</h3>
              {tasks.map((task: any) => (
                <div key={task.id} style={{ padding: '8px', borderBottom: '1px solid #ddd', fontSize: '14px' }}>
                  <strong>{task.title}</strong>: {task.description}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Display regular task list (only if not showing clusters) */}
      {!clusters && data && data.data && (
        <div style={{ marginBottom: '20px' }}>
          <h2>All Tasks</h2>
          {data.data.map((task: any) => (
            <div
              key={task.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '4px',
                padding: '12px',
                marginBottom: '10px',
                backgroundColor: task.completed ? '#f0f0f0' : '#fff',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3 style={{ margin: '0 0 8px 0', textDecoration: task.completed ? 'line-through' : 'none' }}>
                    {task.title}
                  </h3>
                  <p style={{ margin: '0 0 8px 0', color: '#666' }}>
                    {task.description}
                  </p>
                  <small style={{ color: '#999' }}>
                    Created: {new Date(task.created_at).toLocaleString()}
                  </small>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <button
                    onClick={() => {
                      // Open dialog for editing
                      setTaskTitle(task.title);
                      setTaskDescription(task.description);
                      setEditingTaskId(task.id);
                      setOpen(true);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    Update
                  </button>
                  <button
                    onClick={async () => {
                      // Optimistic mark done
                      setData(prev => {
                        if (!prev || !prev.data) return prev;
                        return {
                          ...prev,
                          data: prev.data.map((t: any) => (t.id === task.id ? { ...t, completed: true } : t)),
                        } as ApiResponse;
                      });

                      try {
                        await updateTask(task.id, { completed: true });
                      } catch (err) {
                        console.error('Mark done failed, refreshing list', err);
                        const refreshed = await fetchTasks();
                        setData(refreshed);
                      }
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    Mark Done
                  </button>
                  <button
                    onClick={async () => {
                      // Optimistic delete
                      setData(prev => {
                        if (!prev || !prev.data) return prev;
                        return {
                          ...prev,
                          data: prev.data.filter((t: any) => t.id !== task.id),
                        } as ApiResponse;
                      });

                      try {
                        await deleteTask(task.id);
                      } catch (err) {
                        console.error('Delete failed, refreshing list', err);
                        const refreshed = await fetchTasks();
                        setData(refreshed);
                      }
                    }}
                    style={{ cursor: 'pointer', color: 'red' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <AddNewTaskDialog
        open={open}
        onClose={handleClose}
        onSave={handleSave}
        title={taskTitle}
        description={taskDescription}
        onTitleChange={setTaskTitle}
        onDescriptionChange={setTaskDescription}
      />
    </div>
  );
}

export default App;
