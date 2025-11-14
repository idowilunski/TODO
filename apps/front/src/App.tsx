import { useState, useEffect } from 'react'
import { fetchTasks, ApiResponse, saveNewTask } from './services/api'
import AddNewTaskButton from './components/AddNewTaskButton';
import AddNewTaskDialog from './components/AddNewTaskDialog';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<boolean>(false);
  const handleClose = () => {
    setOpen(false);
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
    fetchData();}
  , []);
    console.log(data, 'my tasks')
  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>My amazing TODO app</h1>

      <AddNewTaskButton onClick={handleOpen} />
      <AddNewTaskDialog open={open} onClose={handleClose} onSave={ async () =>{
        await saveNewTask(
          {
            title: "New Task",
            description: "will do soon"
          }
        );
        handleClose();
      }} />
    </div>
  );
}

export default App;
