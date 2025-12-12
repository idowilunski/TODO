import { useState, useEffect } from 'react';

interface ScheduleTask {
  time: string;
  title: string;
  duration_minutes: number;
}

interface Schedule {
  option_number: number;
  strategy: string;
  tasks: ScheduleTask[];
}

interface Research {
  task_title: string;
  research_findings: string;
  constraints: string[];
}

interface ScheduleData {
  date: string;
  task_count: number;
  research: Research[];
  schedules: Schedule[];
}

export default function Schedules() {
  const [scheduleData, setScheduleData] = useState<ScheduleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSchedule, setSelectedSchedule] = useState<number>(1);
  const userName = "Ido"; // Could come from auth/profile later

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  useEffect(() => {
    fetchSchedules();
    
    // Poll for new schedules every 10 seconds
    const interval = setInterval(() => {
      fetchSchedules();
    }, 10000);
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5001/api/tasks/schedules');
      const data = await response.json();
      
      if (data.status === 'success') {
        setScheduleData(data.data);
        setError(null);
      } else {
        setError(data.message || 'Failed to fetch schedules');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="text-2xl mb-4">☀️</div>
          <div className="text-xl font-medium text-gray-700">Generating your personalized schedules...</div>
          <div className="text-sm text-gray-500 mt-2">This may take a moment</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  if (!scheduleData) {
    return <div>No schedule data available</div>;
  }

  const currentSchedule = scheduleData.schedules.find(
    s => s.option_number === selectedSchedule
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Personalized Morning Greeting */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {getGreeting()}, {userName}! ☀️
          </h1>
          <p className="text-xl text-gray-600">
            Here are some suggested schedules for your day
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Generated on {new Date(scheduleData.date).toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })} • {scheduleData.task_count} tasks organized
          </p>
        </div>

        {/* Schedule Options Tabs */}
        <div className="mb-6 flex gap-4 justify-center">
          {scheduleData.schedules.map((schedule) => (
            <button
              key={schedule.option_number}
              onClick={() => setSelectedSchedule(schedule.option_number)}
              className={`px-8 py-4 rounded-xl font-medium transition-all shadow-md ${
                selectedSchedule === schedule.option_number
                  ? 'bg-blue-600 text-white transform scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 hover:shadow-lg'
              }`}
            >
              <div className="text-lg">Option {schedule.option_number}</div>
              <div className="text-sm font-normal mt-1 opacity-90">
                {schedule.strategy}
              </div>
            </button>
          ))}
        </div>

        {/* Research Summary */}
        {scheduleData.research.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-blue-100">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span>🔍</span> Research Insights
            </h2>
            <div className="space-y-4">
              {scheduleData.research.map((item, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 bg-blue-50 p-3 rounded-r-lg">
                  <h3 className="font-medium text-gray-900">📌 {item.task_title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{item.research_findings}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.constraints.map((constraint, i) => (
                      <span
                        key={i}
                        className="text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium"
                      >
                        {constraint}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Schedule Timeline */}
        {currentSchedule && (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
              <span>📅</span> {currentSchedule.strategy}
            </h2>
            <div className="space-y-3">
              {currentSchedule.tasks.map((task, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-4 p-5 bg-gradient-to-r from-gray-50 to-white rounded-xl hover:shadow-md transition-all border border-gray-100"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                    {idx + 1}
                  </div>
                  <div className="font-mono text-sm text-gray-600 w-40 font-medium">
                    {task.time}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-lg">{task.title}</div>
                    <div className="text-sm text-gray-500 flex items-center gap-1">
                      <span>⏱️</span> {task.duration_minutes} minutes
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <div className="mt-8 text-center">
          <button
            onClick={fetchSchedules}
            disabled={loading}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 font-medium"
          >
            {loading ? '🔄 Regenerating...' : '🔄 Generate New Schedules'}
          </button>
          <p className="text-sm text-gray-500 mt-2">
            Powered by AI • Updates in real-time
          </p>
        </div>
      </div>
    </div>
  );
}
