import React from "react";
import { Composition, registerRoot } from "remotion";
import { WobblyShort, WOBBLY_FRAMES } from "./videos/wobbly/Wobbly";

export const Root: React.FC = () => (
  <Composition id="WobblyShort" component={WobblyShort} durationInFrames={WOBBLY_FRAMES} fps={30} width={1080} height={1920} />
);

export default Root;
