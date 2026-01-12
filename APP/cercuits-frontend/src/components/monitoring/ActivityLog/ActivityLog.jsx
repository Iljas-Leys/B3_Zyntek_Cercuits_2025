import React from 'react';
import './ActivityLog.module.css';

const ActivityLog = ({ activities }) => {
  return (
    <div className="activity-log">
      <h3>Activity Log</h3>
      <ul>
        {activities?.map((activity, index) => (
          <li key={index}>
            <span className="timestamp">{activity.timestamp}</span>
            <span className="message">{activity.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActivityLog;
