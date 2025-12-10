import { useState, useEffect } from 'react'
import { fetchTasks, ApiResponse, saveNewTask, deleteTask, deleteAllTasks, updateTask, seedMockTasks, clusterTasks, researchTask } from './services/api'
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
      // Request LLM-generated mock tasks (source=llm) and create 20 tasks
      const res = await seedMockTasks('llm', 20);
      console.log('seedMockTasks response:', res);
      const updated = await fetchTasks();
      setData(updated);
      // Don't clear clusters - let user see updated count
      // Removed alert popup after seeding
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
  const [researchingTaskId, setResearchingTaskId] = useState<number | null>(null);

  const handleResearch = async (taskId: number) => {
    try {
      setResearchingTaskId(taskId);
      
      // Start research (returns immediately)
      await researchTask(taskId);
      
      // Poll for completion
      const pollInterval = setInterval(async () => {
        const updated = await fetchTasks();
        setData(updated);
        
        const task = updated.data?.find((t: any) => t.id === taskId);
        if (task && (task.research_status === 'completed' || task.research_status === 'failed')) {
          clearInterval(pollInterval);
          setResearchingTaskId(null);
          
          if (task.research_status === 'failed') {
            alert('Research failed: ' + (task.research_result?.error || 'Unknown error'));
          }
        }
      }, 2000);  // Poll every 2 seconds
      
      // Safety timeout after 60 seconds
      setTimeout(() => {
        clearInterval(pollInterval);
        setResearchingTaskId(null);
      }, 60000);
      
    } catch (err) {
      console.error('Research failed:', err);
      alert('Research failed: ' + (err as any).toString());
      setResearchingTaskId(null);
    }
  };

  const handleDeleteAll = async () => {
    if (!window.confirm('Are you sure you want to delete all tasks? This cannot be undone.')) {
      return;
    }
    try {
      // Bulk delete - single API call!
      await deleteAllTasks();
      
      // Refresh list and clear clusters
      const updated = await fetchTasks();
      setData(updated);
      setClusters(null);
    } catch (err) {
      console.error('Delete all failed:', err);
      alert('Failed to delete all tasks: ' + (err as any).toString());
    }
  };
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
        <button 
          onClick={handleDeleteAll}
          style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Delete All Tasks
        </button>
      </div>

      {/* Display clustered tasks */}
      {clusters && (
        <div style={{ marginBottom: '20px', backgroundColor: '#f5f5f5', padding: '15px', borderRadius: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0 }}>Clustered Tasks (by AI)</h2>
            <button 
              onClick={() => setClusters(null)}
              style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              Back to Tasks List
            </button>
          </div>
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
                    onClick={() => handleResearch(task.id)}
                    disabled={researchingTaskId === task.id}
                    style={{ cursor: 'pointer', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', padding: '6px 12px' }}
                  >
                    {researchingTaskId === task.id ? 'Researching...' : '🔍 Research Item'}
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
              {task.research_result && (
                <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#e7f3ff', borderRadius: '4px', borderLeft: '4px solid #007bff' }}>
                  <strong>🤖 Agent Research:</strong>
                  <div style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>
                    {task.research_result.recommendation}
                  </div>
                  <small style={{ color: '#666', marginTop: '8px', display: 'block' }}>
                    Researched at: {new Date(task.research_result.timestamp).toLocaleString()}
                  </small>
                </div>
              )}
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
