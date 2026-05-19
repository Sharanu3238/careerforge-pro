
import { useState } from "react";
import "./App.css";

function App() {

  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);

  // Upload Resume
  const uploadResume = async () => {

    const formData = new FormData();

    formData.append("file", resumeFile);

    const response = await fetch(
      "http://127.0.0.1:8000/upload/",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    setResumeText(data.resume);
  };

  // Analyze Resume
  const analyzeResume = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/analyze/",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            resume: resumeText || "Python SQL FastAPI",
            jd: jd,
          }),
        }
      );

      const data = await response.json();

      setResult(data);

    } catch (error) {

      console.log(error);

      alert("Backend connection failed");
    }
  };

  return (

    <div className="container mt-5">

      <div className="card shadow p-4">

        <h1 className="text-center mb-4">
          AI – Resume ATS Optimizer
        </h1>

        <input
          type="file"
          className="form-control"
          onChange={(e) => setResumeFile(e.target.files[0])}
        />

        <br />

        <button
          className="btn btn-primary"
          onClick={uploadResume}
        >
          Upload Resume
        </button>

        <br />

        <textarea
          rows="8"
          className="form-control"
          placeholder="Paste Job Description"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />

        <br />

        <button
          className="btn btn-success"
          onClick={analyzeResume}
        >
          Analyze Resume
        </button>

        {result && (

          <div className="mt-5">

            <div className="card shadow p-4 mb-4">

              <h2 className="text-center mb-3">
                ATS Score
              </h2>

              <div className="progress mb-3">

                <div
                  className="progress-bar bg-success"
                  role="progressbar"
                  style={{
                    width: `${result.ats_score}%`
                  }}
                >
                  {result.ats_score}%
                </div>

              </div>

            </div>

            <div className="card shadow p-4 mb-4">

              <h3 className="mb-3">
                Keywords Matched
              </h3>

              <pre>
                {JSON.stringify(
                  result.keywords,
                  null,
                  2
                )}
              </pre>

            </div>

            <div className="card shadow p-4">

              <h3 className="mb-3">
                Improved Resume Suggestions
              </h3>

              <p>
                {result.improved_resume}
              </p><br />

<a
  href="http://127.0.0.1:8000/download/"
  target="_blank"
  rel="noreferrer"
>

  <button className="btn btn-primary">
    Download Improved Resume
  </button>

</a>

            </div>

          </div>

        )}

      </div>

    </div>

  );
}

export default App;

