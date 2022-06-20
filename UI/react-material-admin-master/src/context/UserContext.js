import React from "react";
import { authlogin, authregister } from "../components/apis/authentication";

var UserStateContext = React.createContext();
var UserDispatchContext = React.createContext();

function userReducer(state, action) {
  switch (action.type) {
    case "LOGIN_SUCCESS":
      return { ...state, isAuthenticated: true };
    case "SIGN_OUT_SUCCESS":
      return { ...state, isAuthenticated: false };
    default: {
      throw new Error(`Unhandled action type: ${action.type}`);
    }
  }
}

function UserProvider({ children }) {
  var [state, dispatch] = React.useReducer(userReducer, {
    isAuthenticated: !!localStorage.getItem("id_token"),
  });

  return (
    <UserStateContext.Provider value={state}>
      <UserDispatchContext.Provider value={dispatch}>
        {children}
      </UserDispatchContext.Provider>
    </UserStateContext.Provider>
  );
}

function useUserState() {
  var context = React.useContext(UserStateContext);
  if (context === undefined) {
    throw new Error("useUserState must be used within a UserProvider");
  }
  return context;
}

function useUserDispatch() {
  var context = React.useContext(UserDispatchContext);
  if (context === undefined) {
    throw new Error("useUserDispatch must be used within a UserProvider");
  }
  return context;
}

export {
  UserProvider,
  useUserState,
  useUserDispatch,
  loginUser,
  signOut,
  RegisterUser,
};

// ###########################################################

function loginUser(dispatch, login, password, history, setIsLoading, setError) {
  setError(false);
  setIsLoading(true);
  if (!!login && !!password) {
    authlogin(login, password)
      .then((data) => {
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("user_info", login);
        setError(null);
        setIsLoading(false);
        dispatch({ type: "LOGIN_SUCCESS" });
        history.push("/app/dashboard");
      })
      .catch(() => {
        setError(true);
        setIsLoading(false);
        dispatch({ type: "LOGIN_FAILURE" });
      });
  } else {
    dispatch({ type: "LOGIN_FAILURE" });
    setError(true);
    setIsLoading(false);
  }
}

function signOut(dispatch, history) {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  dispatch({ type: "SIGN_OUT_SUCCESS" });
  history.push("/login");
}

function RegisterUser(dispatch, body, history, setIsLoading, setError) {
  setError(false);
  setIsLoading(true);
  if (!!body) {
    authregister(body).then((data) => {
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      setError(null);
      setIsLoading(false);
      dispatch({ type: "LOGIN_SUCCESS" });
      history.push("/app/dashboard");
    });
  } else {
    dispatch({ type: "LOGIN_FAILURE" });
    setError(true);
    setIsLoading(false);
  }
}
