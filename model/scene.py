from typing import List
from dataclasses import dataclass, field

from moviepy.editor import VideoClip, AudioClip, CompositeAudioClip

from formats.utils.scene_builder import arrange_snippets

from model.snippet import Snippet


@dataclass
class Scene:
    snippets: List[Snippet]
    video_clip: VideoClip = None
    audio_clip: AudioClip = None
    arrangement: str = "vertical"
    use_audio: List[int] = field(default_factory=lambda: [0])

    def unpack(self, staging_dir):
        self.snippets = [Snippet(**snippet).unpack(staging_dir) for snippet in self.snippets]
        self.audio_clip = CompositeAudioClip([self.snippets[x].audio.clip for x in self.use_audio])

        built_scene = arrange_snippets(self.snippets, self.arrangement)

        snippet_durations = [
            snippet.video.clip.duration
            for snippet in self.snippets
            if (
                snippet.video
                and snippet.video.clip.duration
                and snippet.video.clip.duration > 0
            )
            or (
                snippet.video
                and snippet.audio
                and snippet.audio.clip
                and snippet.audio.clip.duration
                and snippet.audio.clip.duration > 0
            )
        ]

        if len(snippet_durations) > 0:
            duration = min(snippet_durations)
            duration = min([duration, self.audio_clip.duration])

        if built_scene:
            self.video_clip = (
                built_scene.set_audio(self.audio_clip)
                .set_duration(duration)
                .set_fps(30)
            )

        return self
