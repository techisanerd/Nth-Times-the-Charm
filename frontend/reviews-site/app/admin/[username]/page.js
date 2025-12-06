"use client"

import { use, useEffect, useState } from "react";

export default function AdminPage({ params }) {
  const { username } = use(params);

  const [admin, setUser] = useState(null);
  const [error, setError] = useState(null);



  const [reports, setReports] = useState(null);

 

  useEffect(() => {
    fetch(`/api/Admins/${username}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch user");
        return res.json();
      })
      .then(setUser)
      .catch((err) => setError(err.message));
  }, [admin]);

useEffect(() => {
    fetch(`/api/Reports`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to get reports.");
        return res.json();
      })
      .then(setReports)
      .catch((err) => setError(err.message));
  }, [reports]);



  

  if (error) return <p>Error: {error}</p>;
   if (!admin) return <p>Loading…</p>;
    if(!reports) return <p>Loading...</p>

  return (<div ><h1>Current User: {username}  ----Viewing Reports</h1>
<ul>
        {reports.map((report) => (
          <li key={report.id}>
            <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', fontFamily: 'Arial, sans-serif' }}>
                <b>
                    {report.movie}, {report.reviewTitle}, {report.reporter}, {report.reportDate}, {report.reviewer}
                </b>
                <br/>
                {report.reason}
                <br/>
                <b><a href={"/takedown?reviewer=" + report.reviewer+"&movie="+report.movie+"&title="+report.reviewTitle}>Takedown Review?</a></b>
            </div>
          </li>
        ))}
      </ul>


      </div>
  );
  
} 