// Sandbox entry for the look pass: renders src/videos/wobbly (an isolated copy of the train short).
import React from "react";
import { Composition, registerRoot } from "remotion";
import { WobblyShort, WOBBLY_FRAMES } from "../../videos/wobbly/Wobbly";

const Root: React.FC = () => <Composition id="WobblyShort" component={WobblyShort} durationInFrames={WOBBLY_FRAMES} fps={30} width={1080} height={1920} />;
registerRoot(Root);
