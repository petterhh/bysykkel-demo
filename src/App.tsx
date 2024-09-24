import { useEffect, useState } from "react";
import "./App.css";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Station = {
  id: number;
  name: string;
  address: string;
  numBikesAvailable?: number;
};

function App() {
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [stationData, setStationData] = useState<Record<number, Station>>({});
  const [fullStationData, setFullStationData] = useState<
    Record<number, Station>
  >({});

  useEffect(() => {
    async function fetchStationData() {
      const url =
        "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json";
      const response = await fetch(url, {
        headers: {
          "Client-Identifier": "petter-hohle-bysykkel-demo",
        },
      });
      const responseData = await response.json();
      if (!response.ok) {
        setErrorMessage(response.statusText);
        return;
      }
      const fetchedStationData: Record<number, Station> = Object.fromEntries(
        responseData.data.stations.map((station) => [
          station.station_id,
          {
            id: station.station_id,
            name: station.name,
            address: station.address,
          },
        ])
      );
      setStationData(fetchedStationData);
    }
    fetchStationData();
  }, []);

  useEffect(() => {
    async function fetchAvailabilityData() {
      const availabilityUrl =
        "https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json";
      const availabilityResponse = await fetch(availabilityUrl, {
        headers: {
          "Client-Identifier": "petter-hohle-bysykkel-demo",
        },
      });

      const availabilityResponseData = await availabilityResponse.json();
      if (!availabilityResponse.ok) {
        setErrorMessage(availabilityResponse.statusText);
        return;
      }
      const aggregatedStationData: Record<number, Station> = { ...stationData };
      for (const station of availabilityResponseData.data.stations) {
        if (station.station_id in stationData) {
          aggregatedStationData[station.station_id].numBikesAvailable =
            station.num_bikes_available;
        }
      }
      setFullStationData(aggregatedStationData);
    }
    fetchAvailabilityData();
  }, [stationData]);

  return (
    <>
      <h1>Bysykkel demo</h1>
      {errorMessage ? (
        <div>{errorMessage}</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="text-left">ID</TableHead>
              <TableHead className="text-left">Name</TableHead>
              <TableHead className="text-left">Address</TableHead>
              <TableHead className="text-right">No. bikes available</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Object.values(fullStationData).map((station) => (
              <TableRow key={station.id}>
                <TableCell className="text-left">{station.id}</TableCell>
                <TableCell className="text-left">{station.name}</TableCell>
                <TableCell className="text-left">{station.address}</TableCell>
                <TableCell className="text-right">
                  {station.numBikesAvailable}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </>
  );
}

export default App;
