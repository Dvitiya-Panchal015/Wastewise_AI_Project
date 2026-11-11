
import { useState } from "react";

interface AuthPageProps {
  onLoginSuccess: (token: string) => void;
}

const API_URL = "http://127.0.0.1:8000";

function AuthPage({ onLoginSuccess }: AuthPageProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      const endpoint = isRegister
        ? "/api/auth/register"
        : "/api/auth/login";

      const payload = isRegister
        ? { name, email, password }
        : { email, password };

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Authentication failed"
        );
      }

      if (isRegister) {
        setMessage("Registration successful! Please login.");
        setIsRegister(false);
        setName("");
        setPassword("");
      } else {
        if (!data.access_token) {
          throw new Error("Access token not received from server.");
        }

        onLoginSuccess(data.access_token);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to backend"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          ♻️ WasteWise AI
        </div>

        <h1 style={styles.heading}>
          {isRegister ? "Create Account" : "Welcome Back"}
        </h1>

        <p style={styles.subtitle}>
          {isRegister
            ? "Join WasteWise AI to manage inventory smartly"
            : "Login to access your WasteWise AI dashboard"}
        </p>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div style={styles.field}>
              <label style={styles.label}>Full Name</label>
              <input
                style={styles.input}
                type="text"
                placeholder="Enter your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          )}

          <div style={styles.field}>
            <label style={styles.label}>Email Address</label>
            <input
              style={styles.input}
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </div>

          {error && (
            <p style={styles.error}>{error}</p>
          )}

          {message && (
            <p style={styles.success}>{message}</p>
          )}

          <button
            type="submit"
            style={styles.button}
            disabled={loading}
          >
            {loading
              ? "Please wait..."
              : isRegister
              ? "Create Account"
              : "Login"}
          </button>
        </form>

        <p style={styles.switchText}>
          {isRegister
            ? "Already have an account?"
            : "Don't have an account?"}

          <button
            type="button"
            style={styles.switchButton}
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
              setMessage("");
            }}
          >
            {isRegister ? "Login" : "Register"}
          </button>
        </p>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #102b20, #1c4933, #071b13)",
    padding: "20px",
    fontFamily: "Arial, sans-serif",
  },

  card: {
    width: "100%",
    maxWidth: "420px",
    background: "#ffffff",
    padding: "38px",
    borderRadius: "18px",
    boxShadow: "0 15px 45px rgba(0,0,0,0.25)",
  },

  logo: {
    textAlign: "center",
    color: "#16834a",
    fontSize: "25px",
    fontWeight: "bold",
    marginBottom: "25px",
  },

  heading: {
    textAlign: "center",
    color: "#183b2a",
    marginBottom: "8px",
  },

  subtitle: {
    textAlign: "center",
    color: "#777",
    fontSize: "14px",
    marginBottom: "28px",
  },

  field: {
    marginBottom: "18px",
  },

  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "bold",
    marginBottom: "7px",
    color: "#333",
  },

  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "13px",
    border: "1px solid #d5ddd8",
    borderRadius: "8px",
    fontSize: "14px",
    outline: "none",
  },

  button: {
    width: "100%",
    padding: "14px",
    background: "#16834a",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    marginTop: "8px",
  },

  switchText: {
    textAlign: "center",
    fontSize: "14px",
    color: "#666",
    marginTop: "22px",
  },

  switchButton: {
    background: "none",
    border: "none",
    color: "#16834a",
    fontWeight: "bold",
    cursor: "pointer",
    marginLeft: "6px",
  },

  error: {
    color: "#d32f2f",
    fontSize: "13px",
  },

  success: {
    color: "#16834a",
    fontSize: "13px",
  },
};

export default AuthPage;
