import React, { useEffect, useRef, useState } from "react";
import {
  api,
  getCapCutPackageUrl,
  getExportFileUrl,
  getSpeakerPreviewUrl,
  getSubtitleFileUrl,
  getUploadContentUrl,
  SubtitleResult,
  SubtitleSegment,
  Upload,
  ProcessingOptionsPayload,
  SpeechAnalysis,
} from "../api/client";
import "./VideoEditor.css";

interface Props {
  uploadId: string;
  onBack: () => void;
}

type AspectRatio = "original" | "9:16" | "16:9" | "1:1";
type EditorTool = "capcut" | "premiere" | "resolve" | "final-cut" | "generic";

interface EditSegment {
  id: string;
  start: number;
  end: number;
  comment: string;
}

const DEFAULT_PROCESSING_OPTIONS: ProcessingOptionsPayload = {
  remove_silence: false,
  speed_up_excluded: false,
  excluded_speed: 2,
  assembly_only: false,
  remove_background_music: false,
  add_background_music: false,
  background_music_volume: 0.22,
};

export default function VideoEditor({ uploadId, onBack }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mountedRef = useRef(true);
  const [upload, setUpload] = useState<Upload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentTime, setCurrentTime] = useState(0);
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(0);
  const [segments, setSegments] = useState<EditSegment[]>([]);
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>("original");
  const [message, setMessage] = useState("");
  const [subtitle, setSubtitle] = useState<SubtitleResult | null>(null);
  const [subtitleLanguage, setSubtitleLanguage] = useState("");
  const [subtitleStatus, setSubtitleStatus] = useState("");
  const [subtitleGenerating, setSubtitleGenerating] = useState(false);
  const [speechAnalysis, setSpeechAnalysis] = useState<SpeechAnalysis | null>(
    null
  );
  const [selectedSpeakers, setSelectedSpeakers] = useState<string[]>([]);
  const [selectedSubtitleId, setSelectedSubtitleId] = useState<number | null>(
    null
  );
  const [loopingSubtitleId, setLoopingSubtitleId] = useState<number | null>(
    null
  );
  const [editingSubtitleId, setEditingSubtitleId] = useState<number | null>(
    null
  );
  const [subtitleMenuId, setSubtitleMenuId] = useState<number | null>(null);
  const [subtitleSaving, setSubtitleSaving] = useState(false);
  const [editorTool, setEditorTool] = useState<EditorTool>("capcut");
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState("");
  const [burnSubtitles, setBurnSubtitles] = useState(true);
  const [processingOptions, setProcessingOptions] =
    useState<ProcessingOptionsPayload>(DEFAULT_PROCESSING_OPTIONS);
  const [appliedProcessingOptions, setAppliedProcessingOptions] =
    useState<ProcessingOptionsPayload>(DEFAULT_PROCESSING_OPTIONS);
  const [segmentsBeforeOptions, setSegmentsBeforeOptions] = useState<
    EditSegment[] | null
  >(null);
  const [backgroundMusicFile, setBackgroundMusicFile] = useState<File | null>(
    null
  );
  const [backgroundMusicStatus, setBackgroundMusicStatus] = useState("");

  useEffect(() => {
    mountedRef.current = true;
    setLoading(true);
    api
      .getUpload(uploadId)
      .then((data) => {
        setUpload(data);
        setTrimEnd(data.duration ?? 0);
        const saved = window.localStorage.getItem(`yoko-editor-${uploadId}`);
        if (saved) {
          try {
            const draft = JSON.parse(saved);
            setTrimStart(draft.trimStart ?? 0);
            setTrimEnd(draft.trimEnd ?? data.duration ?? 0);
            setAspectRatio(draft.aspectRatio ?? "original");
            setEditorTool(draft.editorTool ?? "capcut");
            setBurnSubtitles(draft.burnSubtitles ?? true);
            setProcessingOptions({
              ...DEFAULT_PROCESSING_OPTIONS,
              ...(draft.processingOptions ?? {}),
            });
            setAppliedProcessingOptions({
              ...DEFAULT_PROCESSING_OPTIONS,
              ...(draft.appliedProcessingOptions ?? {}),
            });
            setSegments(
              Array.isArray(draft.segments)
                ? draft.segments
                : draft.trimEnd > draft.trimStart
                  ? [
                      {
                        id: createId(),
                        start: draft.trimStart,
                        end: draft.trimEnd,
                        comment: "",
                      },
                    ]
                  : []
            );
          } catch {
            window.localStorage.removeItem(`yoko-editor-${uploadId}`);
          }
        }
      })
      .catch((reason) => {
        setError(reason instanceof Error ? reason.message : "영상을 불러오지 못했습니다.");
      })
      .finally(() => setLoading(false));

    api.getSubtitles(uploadId).then(setSubtitle).catch(() => undefined);
    api
      .getSpeechAnalysis(uploadId)
      .then((analysis) => {
        setSpeechAnalysis(analysis);
        setSelectedSpeakers(
          analysis.speakers
            .filter((speaker) => speaker.selected)
            .map((speaker) => speaker.speaker_id)
        );
      })
      .catch(() => undefined);
    return () => {
      mountedRef.current = false;
    };
  }, [uploadId]);

  const duration = upload?.duration ?? 0;

  const seek = (value: number) => {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    video.currentTime = value;
    setCurrentTime(value);
  };

  const saveDraft = () => {
    window.localStorage.setItem(
      `yoko-editor-${uploadId}`,
      JSON.stringify({
        trimStart,
        trimEnd,
        segments,
        aspectRatio,
        editorTool,
        burnSubtitles,
        processingOptions,
        appliedProcessingOptions,
      })
    );
    setMessage("편집 초안을 저장했습니다.");
  };

  const addSegment = () => {
    if (trimEnd <= trimStart) {
      setMessage("끝점은 시작점보다 뒤에 있어야 합니다.");
      return;
    }
    setSegments((current) => [
      ...current,
      {
        id: createId(),
        start: trimStart,
        end: trimEnd,
        comment: "",
      },
    ]);
    setMessage(`구간 ${segments.length + 1}을 추가했습니다.`);
  };

  const updateSegmentComment = (id: string, comment: string) => {
    setSegments((current) =>
      current.map((segment) =>
        segment.id === id ? { ...segment, comment } : segment
      )
    );
  };

  const removeSegment = (id: string) => {
    setSegments((current) => current.filter((segment) => segment.id !== id));
  };

  const applyProcessingOptions = () => {
    if (processingOptions.remove_silence) {
      if (!subtitle?.segments.length) {
        setMessage("무음 파트 제거를 적용하려면 자동 자막을 먼저 생성해주세요.");
        return;
      }
      if (segmentsBeforeOptions === null) {
        setSegmentsBeforeOptions(segments);
      }
      setSegments(
        subtitle.segments.map((item) => ({
          id: `speech-${item.id}`,
          start: roundTime(item.start),
          end: roundTime(item.end),
          comment: item.text,
        }))
      );
    } else if (segmentsBeforeOptions !== null) {
      setSegments(segmentsBeforeOptions);
      setSegmentsBeforeOptions(null);
    }
    setAppliedProcessingOptions({ ...processingOptions });
    setMessage(
      processingOptions.remove_silence ||
        processingOptions.speed_up_excluded ||
        processingOptions.assembly_only
        ? "선택한 영상 옵션을 재적용했습니다."
        : "적용할 영상 옵션이 없습니다."
    );
  };

  const resetProcessingOptions = () => {
    if (segmentsBeforeOptions !== null) {
      setSegments(segmentsBeforeOptions);
    }
    setSegmentsBeforeOptions(null);
    setProcessingOptions({ ...DEFAULT_PROCESSING_OPTIONS });
    setAppliedProcessingOptions({ ...DEFAULT_PROCESSING_OPTIONS });
    setMessage("영상 옵션과 자동 생성 구간을 초기화했습니다.");
  };

  const analyzeSpeech = async () => {
    setSubtitleGenerating(true);
    setSubtitleStatus("음악과 육성을 분리하고 화자를 분석하는 중...");
    try {
      const job = await api.createSpeechAnalysis(
        uploadId,
        subtitleLanguage || undefined
      );
      await waitForSubtitleJob(job.job_id);
      const analysis = await api.getSpeechAnalysis(uploadId);
      if (mountedRef.current) {
        setSpeechAnalysis(analysis);
        setSelectedSpeakers(
          analysis.speakers
            .filter((speaker) => speaker.selected)
            .map((speaker) => speaker.speaker_id)
        );
        setSubtitleStatus(
          `${analysis.language.toUpperCase()} 화자 ${analysis.speakers.length}개 분석 완료`
        );
      }
    } catch (reason) {
      if (mountedRef.current) {
        setSubtitleStatus(
          reason instanceof Error ? reason.message : "자막 생성에 실패했습니다."
        );
      }
    } finally {
      if (mountedRef.current) {
        setSubtitleGenerating(false);
      }
    }
  };

  const generateSubtitles = async () => {
    if (!speechAnalysis) {
      setSubtitleStatus("먼저 음성·화자 분석을 실행해주세요.");
      return;
    }
    if (selectedSpeakers.length === 0) {
      setSubtitleStatus("자막으로 만들 화자를 한 명 이상 선택해주세요.");
      return;
    }
    setSubtitleGenerating(true);
    setSubtitleStatus("선택한 화자의 육성만 자막으로 생성하는 중...");
    try {
      const job = await api.createSubtitles(
        uploadId,
        subtitleLanguage || undefined,
        selectedSpeakers
      );
      await waitForSubtitleJob(job.job_id);
      const result = await api.getSubtitles(uploadId);
      if (mountedRef.current) {
        setSubtitle(result);
        setSubtitleStatus(
          `${result.language.toUpperCase()} 선택 화자 자막 ${result.segments.length}개 생성 완료`
        );
      }
    } catch (reason) {
      if (mountedRef.current) {
        setSubtitleStatus(
          reason instanceof Error ? reason.message : "자막 생성에 실패했습니다."
        );
      }
    } finally {
      if (mountedRef.current) {
        setSubtitleGenerating(false);
      }
    }
  };

  const toggleSpeaker = (speakerId: string) => {
    setSelectedSpeakers((current) =>
      current.includes(speakerId)
        ? current.filter((item) => item !== speakerId)
        : [...current, speakerId]
    );
  };

  const waitForSubtitleJob = async (jobId: string) => {
    for (;;) {
      await delay(2000);
      const job = await api.getJob(jobId);
      if (job.status === "COMPLETED") {
        return;
      }
      if (job.status === "FAILED" || job.status === "CANCELED") {
        throw new Error(job.metadata.error || `자막 작업 ${job.status}`);
      }
      if (!mountedRef.current) {
        throw new Error("자막 작업 확인을 중단했습니다.");
      }
    }
  };

  const activeSubtitle = subtitle?.segments.find(
    (segment) => currentTime >= segment.start && currentTime <= segment.end
  );
  const selectedSubtitle = subtitle?.segments.find(
    (segment) => segment.id === selectedSubtitleId
  );
  const loopingSubtitle = subtitle?.segments.find(
    (segment) => segment.id === loopingSubtitleId
  );
  const editingSubtitle = subtitle?.segments.find(
    (segment) => segment.id === editingSubtitleId
  );

  const selectSubtitle = (item: SubtitleSegment) => {
    setSelectedSubtitleId(item.id);
    setLoopingSubtitleId(item.id);
    setEditingSubtitleId(null);
    setSubtitleMenuId(null);
    const video = videoRef.current;
    if (!video) {
      return;
    }
    video.currentTime = item.start;
    setCurrentTime(item.start);
    video.play().catch(() => undefined);
  };

  const handleVideoTimeUpdate = (time: number) => {
    setCurrentTime(time);
    if (loopingSubtitle && time >= loopingSubtitle.end) {
      const video = videoRef.current;
      if (video) {
        video.currentTime = loopingSubtitle.start;
        setCurrentTime(loopingSubtitle.start);
        video.play().catch(() => undefined);
      }
    }
  };

  const openSubtitleEditor = (item: SubtitleSegment) => {
    setEditingSubtitleId(item.id);
    setSubtitleMenuId(null);
  };

  const stopSubtitleLoop = () => {
    setLoopingSubtitleId(null);
    setSubtitleMenuId(null);
    setSubtitleStatus("선택한 자막의 반복 재생을 해제했습니다.");
  };

  const updateSubtitle = (
    id: number,
    patch: Partial<Pick<SubtitleSegment, "start" | "end" | "text">>
  ) => {
    setSubtitle((current) =>
      current
        ? {
            ...current,
            segments: current.segments.map((item) =>
              item.id === id ? { ...item, ...patch } : item
            ),
          }
        : current
    );
  };

  const saveSubtitles = async () => {
    if (!subtitle) {
      return;
    }
    setSubtitleSaving(true);
    setSubtitleStatus("수정한 자막을 저장하는 중...");
    try {
      const saved = await api.updateSubtitles(uploadId, subtitle.segments);
      setSubtitle(saved);
      setSubtitleStatus("자막 시간과 문구를 저장했습니다.");
    } catch (reason) {
      setSubtitleStatus(
        reason instanceof Error ? reason.message : "자막 저장에 실패했습니다."
      );
    } finally {
      setSubtitleSaving(false);
    }
  };

  const splitSubtitle = () => {
    if (!subtitle || !selectedSubtitle) {
      return;
    }
    const splitAt =
      currentTime > selectedSubtitle.start && currentTime < selectedSubtitle.end
        ? currentTime
        : (selectedSubtitle.start + selectedSubtitle.end) / 2;
    const textParts = splitText(selectedSubtitle.text);
    const nextSegments = subtitle.segments.flatMap((item) =>
      item.id === selectedSubtitle.id
        ? [
            {
              ...item,
              end: roundTime(splitAt),
              text: textParts[0],
            },
            {
              ...item,
              id: item.id + 0.5,
              start: roundTime(splitAt),
              text: textParts[1],
            },
          ]
        : [item]
    );
    setSubtitle({
      ...subtitle,
      segments: nextSegments.map((item, index) => ({
        ...item,
        id: index + 1,
      })),
    });
    setSelectedSubtitleId(
      nextSegments.findIndex((item) => item.id === selectedSubtitle.id) + 1
    );
    setSubtitleStatus("자막을 두 구간으로 나눴습니다. 저장을 눌러 반영하세요.");
  };

  const createRenderedExport = async (tool: EditorTool) => {
    setExporting(true);
    setExportStatus("편집 결과 렌더링을 시작합니다...");
    try {
      if (appliedProcessingOptions.add_background_music) {
        if (backgroundMusicFile) {
          setExportStatus("배경음악을 업로드하는 중...");
          const uploaded = await api.uploadBackgroundMusic(
            uploadId,
            backgroundMusicFile
          );
          setBackgroundMusicStatus(`${uploaded.filename} 업로드 완료`);
        } else if (!backgroundMusicStatus) {
          throw new Error("추가할 배경음악 파일을 먼저 선택해주세요.");
        }
      }
      const job = await api.createExport(uploadId, {
        aspect_ratio: aspectRatio,
        editor_tool: tool,
        segments,
        burn_subtitles: burnSubtitles,
        processing_options: appliedProcessingOptions,
      });
      const completed = await waitForJob(job.job_id, "렌더링");
      setExportStatus("렌더링 완료");
      return completed.job_id;
    } finally {
      setExporting(false);
    }
  };

  const waitForJob = async (jobId: string, label: string) => {
    for (;;) {
      await delay(2000);
      const job = await api.getJob(jobId);
      if (job.status === "COMPLETED") {
        return job;
      }
      if (job.status === "FAILED" || job.status === "CANCELED") {
        throw new Error(job.metadata.error || `${label} 작업 ${job.status}`);
      }
      setExportStatus(`${label} 중... (${job.status})`);
    }
  };

  const downloadRenderedVideo = async () => {
    try {
      const exportId = await createRenderedExport(editorTool);
      triggerDownload(getExportFileUrl(uploadId, exportId));
    } catch (reason) {
      setExportStatus(
        reason instanceof Error ? reason.message : "영상 렌더링에 실패했습니다."
      );
    }
  };

  const sendToCapCut = async () => {
    const capcutWindow = window.open("about:blank", "_blank");
    try {
      const exportId = await createRenderedExport("capcut");
      triggerDownload(getCapCutPackageUrl(uploadId, exportId));
      if (capcutWindow) {
        capcutWindow.location.href = "https://www.capcut.com/editor";
      }
      setExportStatus(
        "CapCut 패키지를 다운로드했습니다. 열린 CapCut에서 MP4와 SRT를 가져오세요."
      );
    } catch (reason) {
      capcutWindow?.close();
      setExportStatus(
        reason instanceof Error ? reason.message : "CapCut 내보내기에 실패했습니다."
      );
    }
  };

  if (loading) {
    return <main className="editor-shell">편집기를 불러오는 중...</main>;
  }

  if (error || !upload) {
    return (
      <main className="editor-shell">
        <button className="btn-secondary" onClick={onBack}>
          프로젝트로 돌아가기
        </button>
        <p className="editor-error">{error || "업로드 정보를 찾을 수 없습니다."}</p>
      </main>
    );
  }

  return (
    <main className="editor-shell">
      <header className="editor-header">
        <div>
          <button className="btn-secondary" onClick={onBack}>
            ← 프로젝트
          </button>
          <p className="editor-kicker">{upload.project_name}</p>
          <h1>{upload.filename}</h1>
        </div>
        <button className="btn-primary" onClick={saveDraft}>
          초안 저장
        </button>
      </header>

      <section className="editor-workspace">
        <div
          className={[
            "preview-stage",
            `ratio-${aspectRatio.replace(":", "-")}`,
            appliedProcessingOptions.assembly_only ? "assembly-focus" : "",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          <div className="video-frame">
            <video
              ref={videoRef}
              src={getUploadContentUrl(uploadId)}
              controls
              playsInline
              onTimeUpdate={(event) =>
                handleVideoTimeUpdate(event.currentTarget.currentTime)
              }
            />
            {activeSubtitle && (
              <div className="subtitle-overlay">{activeSubtitle.text}</div>
            )}
          </div>
        </div>

        <aside className="editor-sidebar">
          <section className="video-options">
            <h2>영상 옵션</h2>
            <label className="option-check">
              <input
                type="checkbox"
                checked={processingOptions.remove_silence}
                onChange={(event) =>
                  setProcessingOptions((current) => ({
                    ...current,
                    remove_silence: event.target.checked,
                  }))
                }
              />
              <span>
                <strong>무음 파트 제거</strong>
                <small>자막의 음성 구간만 남기고 문구를 코멘트로 사용</small>
              </span>
            </label>

            <div className="option-with-select">
              <label className="option-check">
                <input
                  type="checkbox"
                  checked={processingOptions.speed_up_excluded}
                  onChange={(event) =>
                    setProcessingOptions((current) => ({
                      ...current,
                      speed_up_excluded: event.target.checked,
                    }))
                  }
                />
                <span>
                  <strong>제외부분 배속 적용</strong>
                  <small>선택 구간 밖의 영상을 삭제하지 않고 빠르게 연결</small>
                </span>
              </label>
              <select
                aria-label="제외부분 배속"
                value={processingOptions.excluded_speed}
                disabled={!processingOptions.speed_up_excluded}
                onChange={(event) =>
                  setProcessingOptions((current) => ({
                    ...current,
                    excluded_speed: Number(event.target.value) as 2 | 4 | 8 | 16,
                  }))
                }
              >
                <option value={2}>x2</option>
                <option value={4}>x4</option>
                <option value={8}>x8</option>
                <option value={16}>x16</option>
              </select>
            </div>

            <label className="option-check">
              <input
                type="checkbox"
                checked={processingOptions.assembly_only}
                onChange={(event) =>
                  setProcessingOptions((current) => ({
                    ...current,
                    assembly_only: event.target.checked,
                  }))
                }
              />
              <span>
                <strong>조립만 추출</strong>
                <small>선택 구간의 중앙 작업부를 확대해 화면 비율에 맞춤</small>
              </span>
            </label>

            <label className="option-check">
              <input
                type="checkbox"
                checked={processingOptions.remove_background_music}
                onChange={(event) =>
                  setProcessingOptions((current) => ({
                    ...current,
                    remove_background_music: event.target.checked,
                  }))
                }
              />
              <span>
                <strong>배경음악 제거</strong>
                <small>최종 오디오에서 음성을 강화하고 배경음을 낮춤</small>
              </span>
            </label>

            <div className="background-music-option">
              <label className="option-check">
                <input
                  type="checkbox"
                  checked={processingOptions.add_background_music}
                  onChange={(event) =>
                    setProcessingOptions((current) => ({
                      ...current,
                      add_background_music: event.target.checked,
                    }))
                  }
                />
                <span>
                  <strong>배경음악 추가</strong>
                  <small>선택한 음악을 결과 영상에 낮은 볼륨으로 믹스</small>
                </span>
              </label>
              <input
                type="file"
                accept="audio/*"
                disabled={!processingOptions.add_background_music}
                onChange={(event) => {
                  setBackgroundMusicFile(event.target.files?.[0] ?? null);
                  setBackgroundMusicStatus("");
                }}
              />
              <label className="volume-control">
                배경음악 볼륨{" "}
                {Math.round(processingOptions.background_music_volume * 100)}%
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={processingOptions.background_music_volume}
                  disabled={!processingOptions.add_background_music}
                  onChange={(event) =>
                    setProcessingOptions((current) => ({
                      ...current,
                      background_music_volume: Number(event.target.value),
                    }))
                  }
                />
              </label>
              {backgroundMusicFile && (
                <small className="option-note">
                  선택됨: {backgroundMusicFile.name}
                </small>
              )}
              {backgroundMusicStatus && (
                <small className="option-note">{backgroundMusicStatus}</small>
              )}
            </div>

            <div className="video-option-actions">
              <button className="btn-primary" onClick={applyProcessingOptions}>
                영상 재적용
              </button>
              <button className="btn-secondary" onClick={resetProcessingOptions}>
                초기화
              </button>
            </div>
          </section>

          <div className="output-settings">
          <h2>출력 설정</h2>
          <label htmlFor="aspect-ratio">화면 비율</label>
          <select
            id="aspect-ratio"
            value={aspectRatio}
            onChange={(event) => setAspectRatio(event.target.value as AspectRatio)}
          >
            <option value="original">원본</option>
            <option value="9:16">쇼츠 9:16</option>
            <option value="16:9">가로 16:9</option>
            <option value="1:1">정사각형 1:1</option>
          </select>

          <label htmlFor="editor-tool">편집 도구</label>
          <select
            id="editor-tool"
            value={editorTool}
            onChange={(event) => setEditorTool(event.target.value as EditorTool)}
          >
            <option value="capcut">CapCut (MP4 + SRT)</option>
            <option value="premiere">Adobe Premiere Pro (MP4 + SRT)</option>
            <option value="resolve">DaVinci Resolve (MP4 + SRT)</option>
            <option value="final-cut">Final Cut Pro (MP4 + SRT)</option>
            <option value="generic">일반 편집기 (MP4 + SRT/VTT)</option>
          </select>
          <p className="preset-note">{EDITOR_PRESETS[editorTool]}</p>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={burnSubtitles}
              onChange={(event) => setBurnSubtitles(event.target.checked)}
            />
            영상에 자막 입히기
          </label>

          <dl className="media-summary">
            <div>
              <dt>해상도</dt>
              <dd>
                {upload.metadata.video.width}x{upload.metadata.video.height}
              </dd>
            </div>
            <div>
              <dt>코덱</dt>
              <dd>{upload.metadata.video.codec}</dd>
            </div>
            <div>
              <dt>길이</dt>
              <dd>{formatTime(duration)}</dd>
            </div>
          </dl>
          {message && <p className="editor-message">{message}</p>}
          </div>
        </aside>
      </section>

      <section className="timeline-panel">
        <div className="timeline-heading">
          <div>
            <h2>구간 편집</h2>
            <p>
              현재 {formatTime(currentTime)} / 전체 {formatTime(duration)}
            </p>
          </div>
          <div className="timeline-actions">
            <button
              className="btn-secondary"
              onClick={() => setTrimStart(Math.min(currentTime, trimEnd))}
            >
              현재 위치를 시작점으로
            </button>
            <button
              className="btn-secondary"
              onClick={() => setTrimEnd(Math.max(currentTime, trimStart))}
            >
              현재 위치를 끝점으로
            </button>
            <button className="btn-primary" onClick={addSegment}>
              구간 추가
            </button>
          </div>
        </div>

        <input
          className="timeline-range"
          type="range"
          min="0"
          max={duration}
          step="0.01"
          value={currentTime}
          onChange={(event) => seek(Number(event.target.value))}
        />

        <div className="trim-values">
          <span>시작 {formatTime(trimStart)}</span>
          <span>선택 구간 {formatTime(Math.max(0, trimEnd - trimStart))}</span>
          <span>끝 {formatTime(trimEnd)}</span>
        </div>

        <div className="segment-list">
          <div className="section-title">
            <h3>편집 구간 {segments.length}개</h3>
          </div>
          {segments.length === 0 ? (
            <p className="empty-state">
              시작점과 끝점을 지정한 뒤 구간 추가를 눌러주세요.
            </p>
          ) : (
            segments.map((segment, index) => (
              <article className="segment-card" key={segment.id}>
                <button
                  className="segment-time"
                  onClick={() => seek(segment.start)}
                >
                  구간 {index + 1} · {formatTime(segment.start)} -{" "}
                  {formatTime(segment.end)}
                </button>
                <textarea
                  value={segment.comment}
                  placeholder="이 구간에 대한 코멘트를 입력하세요."
                  onChange={(event) =>
                    updateSegmentComment(segment.id, event.target.value)
                  }
                />
                <button
                  className="btn-danger segment-delete"
                  onClick={() => removeSegment(segment.id)}
                >
                  삭제
                </button>
              </article>
            ))
          )}
        </div>
      </section>

      <section className="subtitle-panel">
        <div className="subtitle-header">
          <div>
            <h2>자동 자막</h2>
            <p>Faster-Whisper가 음성을 분석해 SRT, VTT, JSON을 생성합니다.</p>
          </div>
          <div className="subtitle-controls">
            <select
              aria-label="자막 언어"
              value={subtitleLanguage}
              onChange={(event) => setSubtitleLanguage(event.target.value)}
              disabled={subtitleGenerating}
            >
              <option value="">언어 자동 감지</option>
              <option value="ko">한국어</option>
              <option value="en">English</option>
              <option value="ja">日本語</option>
              <option value="zh">中文</option>
            </select>
            <button
              className="btn-secondary"
              onClick={analyzeSpeech}
              disabled={subtitleGenerating}
            >
              {subtitleGenerating ? "분석 중..." : "음성·화자 분석"}
            </button>
            <button
              className="btn-primary"
              onClick={generateSubtitles}
              disabled={subtitleGenerating || !speechAnalysis}
            >
              선택 화자 자막 생성
            </button>
          </div>
        </div>
        {subtitleStatus && <p className="subtitle-status">{subtitleStatus}</p>}
        {speechAnalysis && (
          <div className="speaker-panel">
            <div className="speaker-panel-heading">
              <h3>화자 선택</h3>
              <span>노래/음악 후보는 기본 제외됩니다.</span>
            </div>
            <div className="speaker-grid">
              {speechAnalysis.speakers.map((speaker) => (
                <article
                  className={[
                    "speaker-card",
                    speaker.content_type === "music" ? "music-candidate" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  key={speaker.speaker_id}
                >
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedSpeakers.includes(speaker.speaker_id)}
                      onChange={() => toggleSpeaker(speaker.speaker_id)}
                    />
                    <span>
                      <strong>{speaker.label}</strong>
                      <small>
                        {speaker.segment_count}개 구간 ·{" "}
                        {formatTime(speaker.duration)}
                      </small>
                    </span>
                  </label>
                  <audio
                    controls
                    preload="none"
                    src={getSpeakerPreviewUrl(uploadId, speaker.speaker_id)}
                  />
                </article>
              ))}
            </div>
          </div>
        )}
        {subtitle && (
          <>
            <div className="subtitle-downloads">
              <a href={getSubtitleFileUrl(uploadId, "srt")}>SRT 다운로드</a>
              <a href={getSubtitleFileUrl(uploadId, "vtt")}>VTT 다운로드</a>
              <a href={getSubtitleFileUrl(uploadId, "json")}>JSON 다운로드</a>
            </div>
            <div className="subtitle-list">
              {subtitle.segments.map((item) => {
                const isSelected = selectedSubtitleId === item.id;
                const isLooping = loopingSubtitleId === item.id;
                const isMenuOpen = subtitleMenuId === item.id;

                return (
                  <div className="subtitle-item" key={item.id}>
                    <button
                      className={[
                        "subtitle-row",
                        activeSubtitle?.id === item.id ? "active" : "",
                        isSelected ? "selected" : "",
                        isLooping ? "looping" : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      onClick={() => selectSubtitle(item)}
                    >
                      <span>
                        {formatTime(item.start)} - {formatTime(item.end)}
                      </span>
                      <strong>{item.text}</strong>
                    </button>
                    {isSelected && (
                      <div className="subtitle-menu-anchor">
                        <button
                          className="subtitle-menu-trigger"
                          aria-label="선택 자막 메뉴"
                          aria-expanded={isMenuOpen}
                          onClick={() =>
                            setSubtitleMenuId(isMenuOpen ? null : item.id)
                          }
                        >
                          <span />
                          <span />
                          <span />
                        </button>
                        {isMenuOpen && (
                          <div className="subtitle-floating-menu">
                            <button onClick={() => openSubtitleEditor(item)}>
                              자막 수정
                            </button>
                            <button
                              onClick={stopSubtitleLoop}
                              disabled={!isLooping}
                            >
                              {isLooping ? "반복 재생 해제" : "반복 해제됨"}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            {editingSubtitle && (
              <div className="subtitle-editor">
                <div className="subtitle-editor-heading">
                  <h3>선택 자막 편집</h3>
                  <span>
                    {formatPreciseTime(editingSubtitle.start)} -{" "}
                    {formatPreciseTime(editingSubtitle.end)}
                  </span>
                </div>
                <div className="subtitle-time-inputs">
                  <label>
                    시작 초
                    <input
                      type="number"
                      min="0"
                      max={editingSubtitle.end}
                      step="0.01"
                      value={editingSubtitle.start}
                      onChange={(event) => {
                        const start = Number(event.target.value);
                        updateSubtitle(editingSubtitle.id, { start });
                        seek(start);
                      }}
                    />
                  </label>
                  <label>
                    종료 초
                    <input
                      type="number"
                      min={editingSubtitle.start}
                      max={duration}
                      step="0.01"
                      value={editingSubtitle.end}
                      onChange={(event) =>
                        updateSubtitle(editingSubtitle.id, {
                          end: Number(event.target.value),
                        })
                      }
                    />
                  </label>
                </div>
                <label>
                  자막 문구
                  <textarea
                    value={editingSubtitle.text}
                    onChange={(event) =>
                      updateSubtitle(editingSubtitle.id, {
                        text: event.target.value,
                      })
                    }
                  />
                </label>
                <div className="subtitle-edit-actions">
                  <button className="btn-secondary" onClick={splitSubtitle}>
                    재생 위치에서 두 개로 나누기
                  </button>
                  <button
                    className="btn-primary"
                    onClick={saveSubtitles}
                    disabled={subtitleSaving}
                  >
                    {subtitleSaving ? "저장 중..." : "자막 수정 저장"}
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </section>

      <section className="export-panel">
        <div>
          <h2>작업 완료</h2>
          <p>
            선택한 편집 구간과 수정된 자막으로 결과물을 생성합니다.
          </p>
          {exportStatus && <p className="export-status">{exportStatus}</p>}
        </div>
        <div className="export-actions">
          <button
            className="btn-capcut"
            onClick={sendToCapCut}
            disabled={exporting}
          >
            CapCut
          </button>
          <button
            className="btn-primary"
            onClick={downloadRenderedVideo}
            disabled={exporting}
          >
            {exporting ? "렌더링 중..." : "Download"}
          </button>
        </div>
      </section>
    </main>
  );
}

function createId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

function delay(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function formatTime(seconds: number) {
  const safe = Number.isFinite(seconds) ? Math.max(0, seconds) : 0;
  const minutes = Math.floor(safe / 60);
  const remainder = Math.floor(safe % 60);
  return `${minutes}:${remainder.toString().padStart(2, "0")}`;
}

function formatPreciseTime(seconds: number) {
  return `${formatTime(seconds)}.${Math.round((seconds % 1) * 100)
    .toString()
    .padStart(2, "0")}`;
}

function roundTime(seconds: number) {
  return Math.round(seconds * 1000) / 1000;
}

function splitText(text: string): [string, string] {
  const words = text.trim().split(/\s+/);
  if (words.length < 2) {
    return [text, text];
  }
  const middle = Math.ceil(words.length / 2);
  return [words.slice(0, middle).join(" "), words.slice(middle).join(" ")];
}

function triggerDownload(url: string) {
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
}

const EDITOR_PRESETS: Record<EditorTool, string> = {
  capcut: "UTF-8 SRT를 CapCut Desktop/Web의 Captions 메뉴에서 가져옵니다.",
  premiere: "MP4와 SRT를 가져온 뒤 SRT를 캡션 트랙으로 배치합니다.",
  resolve: "MP4와 SRT를 Media Pool에 가져와 타임라인에 배치합니다.",
  "final-cut": "MP4를 가져오고 SRT를 캡션 소스로 사용합니다.",
  generic: "MP4, SRT, VTT, JSON 중 편집기가 지원하는 형식을 사용합니다.",
};
