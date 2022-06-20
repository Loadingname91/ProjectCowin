import React, { useState, useEffect } from "react";
import PageTitle from "../../components/PageTitle/PageTitle";

import {
  Button,
  Grid,
  CardContent,
  CardMedia,
  Card,
  CircularProgress,
} from "@material-ui/core";
import { Typography } from "../../components/Wrappers/Wrappers";

// styles
import useStyles from "./styles";
import { useTheme } from "@material-ui/styles";

export default function FaqCenter(props) {
  const [faqData, setFaqData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  var classes = useStyles();

  function formatDate(date) {
    const d = new Date(date);
    const month = `0${d.getMonth() + 1}`.slice(-2);
    const day = `0${d.getDate()}`.slice(-2);
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  }

  useEffect(() => {
    fetch(`http://localhost:8000/api/faq/`, {
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
        setFaqData(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log("API exception", err);
        setError(err);
        setIsLoading(true);
      });
  }, []);

  function renderFAQInfo() {
    return faqData.map((faq, idx) => (
      <Grid item xs={12} sm={6} md={4}>
        <Card className={classes.card}>
          <CardContent className={classes.cardContent}>
            <Typography gutterBottom variant="h3" component="h2">
              {idx + 1}.{faq.question}
            </Typography>

            <Typography gutterBottom variant="h5" component="h5">
              Answer: {faq.answer}
            </Typography>
            <Typography>
              Date Updated : {formatDate(faq.dateupdated)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    ));
  }
  return (
    <>
      <PageTitle title="Frequently Asked Questions" />
      {isLoading || faqData.length === 0 ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={3}>
          {renderFAQInfo()}
        </Grid>
      )}
    </>
  );
}
