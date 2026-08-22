import { NextPageContext } from "next";
import React from "react";

interface ErrorProps {
  statusCode?: number;
}

const ErrorPage = ({ statusCode }: ErrorProps): JSX.Element => {
  return (
    <p>
      {statusCode
        ? `Ocurrió un error ${statusCode} en el servidor`
        : "Ocurrió un error en el cliente"}
    </p>
  );
};

ErrorPage.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  return { statusCode };
};

export default ErrorPage;
