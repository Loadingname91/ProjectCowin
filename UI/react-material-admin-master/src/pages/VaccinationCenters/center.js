import React, { useState, useEffect, useReducer } from "react";
import PageTitle from "../../components/PageTitle/PageTitle";

import {
  Button,
  Grid,
  CardContent,
  CardMedia,
  Card,
  CircularProgress,
} from "@material-ui/core";
import { Typography } from "../../components/Wrappers";

// styles
import useStyles from "./styles";
import { useTheme } from "@material-ui/styles";
import { check } from "prettier";

export default function VaccinationCenter(props) {
  const [isLoading, setIsLoading] = useState(true);
  const [memberLoading, setMemberLoading] = useState(true);
  const [error, setError] = useState(null);
  const [personalData, setpersonalData] = useState([]);

  var classes = useStyles();
  var theme = useTheme();
  const checkingNull = Object.hasOwnProperty.call(
    props.history,
    "vaccinationCenter",
  )
    ? props.history.vaccinationCenter
    : null;
  if (!checkingNull) {
    console.log(props.history);
  }

  useEffect(() => {
    if (props.history.vaccinationCenter) {
      handleDispatch(props.history.vaccinationCenter);
    } else {
      fetch(`http://localhost:8000/api/vaccination_center_all/`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
      })
        .then((res) => {
          if (res.status !== 200) {
            throw new Error("Something went wrong on api server!");
          }
          return res.json();
        })
        .then((data) => {
          handleDispatch(data);
          setIsLoading(false);
        })
        .catch((err) => {
          console.log("API exception", err);
          setError(err);
          setIsLoading(true);
        });
    }
  }, [props.history.vaccinationCenter]);

  const reducer = (state, action) => {
    if (action.type === "set_vaccination_center") {
      return {
        ...state,
        vaccinationCenter: action.payload,
      };
    }
  };

  const [vaccinationCenter, dispatch] = useReducer(reducer, []);

  const handleDispatch = (action) => {
    dispatch({ type: "set_vaccination_center", payload: action });
  };

  useEffect(() => {
    fetch("http://localhost:8000/api/members/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    })
      .then((res) => {
        if (res.status !== 200) {
          throw new Error("Something went wrong on api server!");
        }
        return res.json();
      })
      .then((data) => {
        setpersonalData(data);
      })
      .catch((err) => {
        console.log("API exception", err);
        setError(err);
        setIsLoading(true);
      });
  }, [vaccinationCenter]);

  function formatDate() {
    var d = new Date(),
      month = "" + (d.getMonth() + 1),
      day = "" + d.getDate(),
      year = d.getFullYear();

    if (month.length < 2) month = "0" + month;
    if (day.length < 2) day = "0" + day;

    return [year, month, day].join("-");
  }

  function submit(id) {
    fetch("http://localhost:8000/api/add_self_vaccination_center/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
      body: JSON.stringify({
        center: id,
        date: formatDate(),
      }),
    })
      .then((res) => {
        if (res.status !== 200) {
          throw new Error("Something went wrong on api server!");
        }
        return res.json();
      })
      .then(
        (data) => {
          if (
            data.hasOwnProperty("message") ||
            data.message === "User not registered" ||
            data.message ===
              "User already has registered to a vaccination center"
          ) {
            window.alert(data.message);
          } else {
            window.alert("Vaccination center booked successfully!");
          }
        },
        (err) => {
          window.alert("API exception", err);
          console.log("API exception", err);
          setError(err);
          setIsLoading(true);
        },
      );
  }
  function validateBooked(vaccinationCenter) {
    if (personalData.length > 0 && !!vaccinationCenter) {
      let value = personalData.some((item) => {
        if (
          Object.keys(item).includes("center_registered") &&
          item.center_registered.center_name === vaccinationCenter.name
        ) {
          return true;
        }
        return false;
      });

      return (
        vaccinationCenter.seats_available === 0 ||
        personalData.some((item) => {
          if (
            Object.keys(item).includes("center_registered") &&
            item.center_registered.center_name === vaccinationCenter.name
          ) {
            return true;
          }
          return false;
        })
      );
    }
    return false;
  }

  function renderVaccinationCenter() {
    console.log(vaccinationCenter);
    return vaccinationCenter.vaccinationCenter.map((vaccinationCenter, idx) => (
      <Grid item xs={12} sm={6} md={4}>
        <Card className={classes.card}>
          <CardContent className={classes.cardContent}>
            <Typography gutterBottom variant="h5" component="h2">
              {vaccinationCenter.name}
            </Typography>
            <Typography>{vaccinationCenter.address}</Typography>
            <Typography>{vaccinationCenter.country}</Typography>
            <Typography>{vaccinationCenter.state}</Typography>
            <Typography>{vaccinationCenter.district}</Typography>
            <Typography>{vaccinationCenter.contact}</Typography>
            <Typography>{vaccinationCenter.pin_code}</Typography>
            <Typography variant="h5">
              Seats available : {vaccinationCenter.seats_available}
            </Typography>
            <Button
              onClick={() => submit(vaccinationCenter.id)}
              variant="contained"
              size="medium"
              color="secondary"
              disabled={validateBooked(vaccinationCenter)}
            >
              {validateBooked(vaccinationCenter) ? "Booked" : "Book"}
            </Button>
          </CardContent>
        </Card>
      </Grid>
    ));
  }
  console.log("data ", props.vaccinationCenter, checkingNull);

  console.log("lodaing", vaccinationCenter);
  return (
    <>
      <PageTitle title="Vaccination Center" />
      {isLoading ||
      vaccinationCenter.vaccinationCenter.length === 0 ||
      personalData.length === 0 ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={3}>
          {renderVaccinationCenter()}
        </Grid>
      )}
    </>
  );
}
